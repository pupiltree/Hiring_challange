import json
from typing import Dict, Any, Optional, List

class State:
    def __init__(self, name: str, config: Dict[str, Any], user_slots: Dict[str, Any]):
        self.name = name
        self.slots = user_slots.copy()
        self.prompt = config.get("prompt")
        self.action = config.get("action")
        self.transitions = config.get("transitions", [])

class LangGraph:
    def __init__(self, config: Dict[str, Any]):
        # config: contains 'states' list and 'initial_state'
        self.states_cfg = {s['name']: s for s in config['states']}
        self.initial = config['initial_state']
        # user_id -> (state_name, slots dict)
        self.user_states: Dict[str, (str, Dict[str, Any])] = {}

    @classmethod
    def from_json(cls, path: str) -> 'LangGraph':
        with open(path, 'r') as f:
            cfg = json.load(f)
        return cls(cfg)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'LangGraph':
        return cls(d)

    def set_state(self, user_id: str, state_name: str, slots: Dict[str, Any]):
        # manually override a user's stored state
        self.user_states[user_id] = (state_name, slots.copy())

    def next_state(self, user_id: str, user_input: str) -> State:
        # retrieve or initialize
        state_name, slots = self.user_states.get(user_id, (self.initial, {}))
        cfg = self.states_cfg[state_name]
        # try transitions
        user_input_lc = user_input.strip().lower()
        for tr in cfg.get('transitions', []):
            if tr['on'] in user_input_lc:
                next_name = tr['to']
                slots = {}  # reset slots on transition
                self.user_states[user_id] = (next_name, slots)
                return self.next_state(user_id, user_input)
        # no transition triggered => stay or perform action
        # return current state object
        return State(state_name, cfg, slots)

    def complete_action(self, user_id: str, slot_name: str, slot_value: Any):
        # after action, inject slot into current state
        state_name, slots = self.user_states.get(user_id, (self.initial, {}))
        slots = slots.copy()
        slots[slot_name] = slot_value
        self.user_states[user_id] = (state_name, slots)

    def current_prompt(self, user_id: str) -> Optional[str]:
        state_name, slots = self.user_states.get(user_id, (self.initial, {}))
        cfg = self.states_cfg[state_name]
        prompt = cfg.get('prompt')
        if prompt:
            return prompt.format(**slots)
        return None
