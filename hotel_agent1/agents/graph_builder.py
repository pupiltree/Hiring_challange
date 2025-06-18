from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from typing import TypedDict, Annotated, List
import operator
from agents.hotel_agent import HotelAgent

class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    user_id: str
    current_intent: str
    booking_data: dict
    next_action: str

class HotelGraphBuilder:
    def __init__(self):
        self.agent = HotelAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the conversation flow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_message", self._process_message_node)
        workflow.add_node("handle_booking", self._handle_booking_node)
        workflow.add_node("handle_reschedule", self._handle_reschedule_node)
        workflow.add_node("handle_inquiry", self._handle_inquiry_node)
        workflow.add_node("generate_response", self._generate_response_node)
        
        # Set entry point
        workflow.set_entry_point("process_message")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "process_message",
            self._route_intent,
            {
                "booking": "handle_booking",
                "reschedule": "handle_reschedule", 
                "inquiry": "handle_inquiry",
                "response": "generate_response"
            }
        )
        
        # Connect all handlers to response generation
        workflow.add_edge("handle_booking", "generate_response")
        workflow.add_edge("handle_reschedule", "generate_response")
        workflow.add_edge("handle_inquiry", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _process_message_node(self, state: AgentState):
        """Process incoming message and determine intent"""
        last_message = state["messages"][-1] if state["messages"] else ""
        intent = self.agent.gemini.extract_intent(last_message)
        
        return {
            "current_intent": intent,
            "next_action": intent
        }
    
    def _handle_booking_node(self, state: AgentState):
        """Handle booking-related messages"""
        last_message = state["messages"][-1] if state["messages"] else ""
        response = self.agent._handle_booking_flow(
            self.agent.db.get_conversation_state(state["user_id"]), 
            last_message
        )
        
        return {
            "messages": [response],
            "next_action": "response"
        }
    
    def _handle_reschedule_node(self, state: AgentState):
        """Handle rescheduling messages"""
        last_message = state["messages"][-1] if state["messages"] else ""
        response = self.agent._handle_reschedule_flow(
            self.agent.db.get_conversation_state(state["user_id"]),
            last_message
        )
        
        return {
            "messages": [response],
            "next_action": "response"
        }
    
    def _handle_inquiry_node(self, state: AgentState):
        """Handle general inquiries"""
        last_message = state["messages"][-1] if state["messages"] else ""
        response = self.agent._handle_inquiry(
            self.agent.db.get_conversation_state(state["user_id"]),
            last_message
        )
        
        return {
            "messages": [response],
            "next_action": "response"
        }
    
    def _generate_response_node(self, state: AgentState):
        """Generate final response"""
        return {"next_action": "complete"}
    
    def _route_intent(self, state: AgentState):
        """Route based on detected intent"""
        current_intent = state.get("current_intent", "inquiry")
        
        if current_intent in ["booking"]:
            return "booking"
        elif current_intent in ["reschedule", "cancel"]:
            return "reschedule"
        elif current_intent in ["inquiry", "greeting"]:
            return "inquiry"
        else:
            return "response"
    
    def process(self, user_id: str, message: str) -> str:
        """Process message through the graph"""
        try:
            initial_state = {
                "messages": [message],
                "user_id": user_id,
                "current_intent": "",
                "booking_data": {},
                "next_action": ""
            }
            
            # Run through graph
            result = self.graph.invoke(initial_state)
            
            # Get response from agent directly (simplified approach)
            response = self.agent.process_message(user_id, message)
            return response
            
        except Exception as e:
            print(f"Error in graph processing: {e}")
            return "I'm sorry, I encountered an error. Please try again."