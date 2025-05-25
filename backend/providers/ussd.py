from typing import Dict, Any, Optional, List
import logging
from ..models.notification import USSDMenu, USSDSession
from ..schemas.notification import USSDMenuCreate, USSDSessionCreate

logger = logging.getLogger(__name__)

class USSDProvider:
    def __init__(self):
        self.menus: Dict[str, USSDMenu] = {}
        self.sessions: Dict[str, USSDSession] = {}

    async def create_menu(
        self,
        menu_data: USSDMenuCreate
    ) -> USSDMenu:
        """Create a new USSD menu"""
        try:
            menu = USSDMenu(**menu_data.dict())
            self.menus[menu.id] = menu
            return menu
        except Exception as e:
            logger.error(f"Error creating USSD menu: {str(e)}")
            raise

    async def create_session(
        self,
        session_data: USSDSessionCreate
    ) -> USSDSession:
        """Create a new USSD session"""
        try:
            session = USSDSession(**session_data.dict())
            self.sessions[session.id] = session
            return session
        except Exception as e:
            logger.error(f"Error creating USSD session: {str(e)}")
            raise

    async def handle_request(
        self,
        session_id: str,
        menu_id: str,
        user_input: str,
        phone_number: str
    ) -> str:
        """Handle USSD request and generate response"""
        try:
            # Get or create session
            session = self.sessions.get(session_id)
            if not session:
                session = await self.create_session(
                    USSDSessionCreate(
                        id=session_id,
                        menu_id=menu_id,
                        phone_number=phone_number,
                        current_state="start"
                    )
                )

            # Get menu
            menu = self.menus.get(menu_id)
            if not menu:
                return "Invalid menu. Please try again."

            # Process user input
            response = await self._process_input(session, menu, user_input)
            
            # Update session
            session.current_state = response.get("next_state", session.current_state)
            session.metadata = response.get("metadata", session.metadata)
            
            return response["message"]
        except Exception as e:
            logger.error(f"Error handling USSD request: {str(e)}")
            return "An error occurred. Please try again."

    async def _process_input(
        self,
        session: USSDSession,
        menu: USSDMenu,
        user_input: str
    ) -> Dict[str, Any]:
        """Process user input and generate response"""
        try:
            current_state = session.current_state
            menu_states = menu.states

            # Get current state configuration
            state_config = menu_states.get(current_state)
            if not state_config:
                return {
                    "message": "Invalid state. Please try again.",
                    "next_state": "start"
                }

            # Handle user input based on state type
            if state_config["type"] == "menu":
                return await self._handle_menu_state(state_config, user_input)
            elif state_config["type"] == "input":
                return await self._handle_input_state(state_config, user_input)
            elif state_config["type"] == "confirmation":
                return await self._handle_confirmation_state(state_config, user_input)
            else:
                return {
                    "message": "Invalid state type. Please try again.",
                    "next_state": "start"
                }
        except Exception as e:
            logger.error(f"Error processing USSD input: {str(e)}")
            raise

    async def _handle_menu_state(
        self,
        state_config: Dict[str, Any],
        user_input: str
    ) -> Dict[str, Any]:
        """Handle menu state"""
        try:
            options = state_config.get("options", [])
            
            # Find selected option
            selected_option = next(
                (option for option in options if option["key"] == user_input),
                None
            )
            
            if selected_option:
                return {
                    "message": selected_option.get("response", "Thank you for your selection."),
                    "next_state": selected_option.get("next_state", "start"),
                    "metadata": selected_option.get("metadata", {})
                }
            else:
                return {
                    "message": "Invalid selection. Please try again.",
                    "next_state": state_config.get("state_id", "start")
                }
        except Exception as e:
            logger.error(f"Error handling menu state: {str(e)}")
            raise

    async def _handle_input_state(
        self,
        state_config: Dict[str, Any],
        user_input: str
    ) -> Dict[str, Any]:
        """Handle input state"""
        try:
            # Validate input if validation rules exist
            if "validation" in state_config:
                validation_result = await self._validate_input(
                    user_input,
                    state_config["validation"]
                )
                if not validation_result["is_valid"]:
                    return {
                        "message": validation_result["message"],
                        "next_state": state_config.get("state_id", "start")
                    }

            # Process input
            return {
                "message": state_config.get("success_message", "Input received."),
                "next_state": state_config.get("next_state", "start"),
                "metadata": {
                    "input": user_input,
                    "input_type": state_config.get("input_type", "text")
                }
            }
        except Exception as e:
            logger.error(f"Error handling input state: {str(e)}")
            raise

    async def _handle_confirmation_state(
        self,
        state_config: Dict[str, Any],
        user_input: str
    ) -> Dict[str, Any]:
        """Handle confirmation state"""
        try:
            if user_input.lower() in ["yes", "y", "1"]:
                return {
                    "message": state_config.get("success_message", "Confirmed."),
                    "next_state": state_config.get("success_state", "start"),
                    "metadata": {"confirmed": True}
                }
            elif user_input.lower() in ["no", "n", "2"]:
                return {
                    "message": state_config.get("failure_message", "Cancelled."),
                    "next_state": state_config.get("failure_state", "start"),
                    "metadata": {"confirmed": False}
                }
            else:
                return {
                    "message": "Invalid input. Please enter Yes or No.",
                    "next_state": state_config.get("state_id", "start")
                }
        except Exception as e:
            logger.error(f"Error handling confirmation state: {str(e)}")
            raise

    async def _validate_input(
        self,
        user_input: str,
        validation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate user input against rules"""
        try:
            # Check required
            if validation_rules.get("required", False) and not user_input:
                return {
                    "is_valid": False,
                    "message": "This field is required."
                }

            # Check min length
            if "min_length" in validation_rules and len(user_input) < validation_rules["min_length"]:
                return {
                    "is_valid": False,
                    "message": f"Input must be at least {validation_rules['min_length']} characters."
                }

            # Check max length
            if "max_length" in validation_rules and len(user_input) > validation_rules["max_length"]:
                return {
                    "is_valid": False,
                    "message": f"Input must not exceed {validation_rules['max_length']} characters."
                }

            # Check pattern
            if "pattern" in validation_rules:
                import re
                if not re.match(validation_rules["pattern"], user_input):
                    return {
                        "is_valid": False,
                        "message": validation_rules.get("pattern_message", "Invalid input format.")
                    }

            return {"is_valid": True}
        except Exception as e:
            logger.error(f"Error validating input: {str(e)}")
            raise

    async def update_session(
        self,
        session: USSDSession,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> USSDSession:
        """Update USSD session status"""
        try:
            session.status = status
            if metadata:
                session.metadata = metadata
            return session
        except Exception as e:
            logger.error(f"Error updating USSD session: {str(e)}")
            raise

    async def handle_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming webhook from USSD gateway"""
        try:
            return {
                "session_id": payload.get("sessionId"),
                "phone_number": payload.get("phoneNumber"),
                "service_code": payload.get("serviceCode"),
                "text": payload.get("text"),
                "network_code": payload.get("networkCode")
            }
        except Exception as e:
            logger.error(f"Error handling USSD webhook: {str(e)}")
            raise 