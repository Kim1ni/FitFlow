from typing import Dict, Optional, List

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search, AgentTool, ToolContext
from google.genai import types

from fit_flow.instructions import ORCHESTRATOR_AGENT_INSTRUCTION
from fit_flow.mock_data import MOCK_USER_WARDROBE, MOCK_VENDOR_INVENTORY
from fit_flow.models import InventoryItem, UserWardrobe
from fit_flow.wardrobe.wardrobe_toolset import WardrobeDBToolset

"""
1. Converting the User Dictionary
We loop through your raw dictionary and create objects
"""
users_db: Dict[str, UserWardrobe] = {}
for uid, data in MOCK_USER_WARDROBE.items():
    users_db[uid] = UserWardrobe(**data)

"""
2. Converting the Inventory List
We create a list of objects
"""
inventory_list: List[InventoryItem] = [InventoryItem(**item) for item in MOCK_VENDOR_INVENTORY]

"""
3. OPTIMIZATION: Create a Quick-Lookup Dictionary for IDs
This makes get_item_details instant.
"""
inventory_lookup: Dict[str, InventoryItem] = {
    item.item_id: item for item in inventory_list
}


def get_user_wardrobe(user_id: str) -> Optional[UserWardrobe]:
    """
    Retrieves a user's wardrobe profile including measurements, preferred brands, and fit history.

    Args:
        user_id: Unique identifier for the user (e.g., "user_123")

    Returns:
        Available optional dictionary containing user's measurements, preferred brands, and past fit ratings
    """
    return users_db.get(user_id)  # Returns None if not found, which is safer


def get_item_details(item_id: str) -> Optional[InventoryItem]:
    """
    Retrieves an item object by ID using our optimized lookup dict.

    Args:
        item_id: Unique identifier for the item (e.g., "V001")

    Returns:
        InventoryItem object if found, None otherwise
    """
    return inventory_lookup.get(item_id)


def search_vendor_inventory(
        category: Optional[str] = None,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        color: Optional[str] = None,
        min_condition: int = 3  # Added feature: Filter out bad condition items
) -> List[InventoryItem]:
    """
    Searches inventory using object attributes that match provided criteria.

    Args:
        category: Type of clothing (e.g., "trousers", "shirt", "dress")
        brand: Brand name (e.g., "Zara", "Dockers")
        max_price: Maximum price in KES
        color: Color of the item (e.g., "black", "blue")
        min_condition: Minimum clothing condition(e.g., "1 is bad while 5 is the best")

    Returns:
        List of matching items with full details (measurements, price, etc.)
    """
    results = []

    # loop through an inventory list
    for item in inventory_list:

        if category and item.category != category.lower():
            continue

        if brand and item.brand.lower() != brand.lower():
            continue

        if color and item.color.lower() != color.lower():
            continue

        if max_price is not None and item.price > max_price:
            continue

        if item.condition_score < min_condition:
            continue

        results.append(item)

    return results


def calculate_fit_score(user: UserWardrobe, item: InventoryItem) -> dict:
    """
    Compares user body measurements to item dimensions.
    Returns a dictionary with fit status and a message.

    Args:
        user: User's measurements, fit history, and preferred brands.
        item: Vendor item details with measurements.

    Returns:
        Dictionary containing 'is_match' (bool), 'fit_description' (str), and 'confidence' (str)
        indicating whether the item fits the user and how well
    """
    u_meas = user.measurements
    i_meas = item.measurements

    # Default response
    result = {
        "is_match": False,
        "fit_description": "Unknown category or missing data",
        "confidence": "low"
    }

    # --- LOGIC FOR TROUSERS ---
    if item.category == "trousers":
        if u_meas.waist and i_meas.waist:
            # Logic: Pants usually match if an item waist is equal or up to 1 inch larger than the body
            diff = i_meas.waist - u_meas.waist

            if 0 <= diff <= 1.5:
                result = {"is_match": True, "fit_description": "Good fit (Waist)", "confidence": "high"}
            elif diff > 1.5:
                result = {"is_match": False, "fit_description": "Too loose", "confidence": "high"}
            else:
                result = {"is_match": False, "fit_description": "Too tight", "confidence": "high"}

    # --- LOGIC FOR SHIRTS/JACKETS ---
    elif item.category in ["shirt", "jacket", "dress"]:
        if u_meas.chest and i_meas.chest:
            # Logic: Shirts need "ease". The garment must be 2-4 inches bigger than the body.
            ease = i_meas.chest - u_meas.chest

            if 1.5 <= ease <= 5:
                result = {"is_match": True, "fit_description": "Comfortable fit", "confidence": "high"}
            elif ease > 5:
                result = {"is_match": True, "fit_description": "Oversized/Loose fit", "confidence": "medium"}
            elif 0 <= ease < 1.5:
                result = {"is_match": False, "fit_description": "Skin tight / Slim fit", "confidence": "high"}
            else:
                result = {"is_match": False, "fit_description": "Too small", "confidence": "high"}

    # --- LOGIC FOR SHOES ---
    elif item.category == "shoes":
        if u_meas.foot_length and i_meas.foot_length:
            # Logic: Shoes need to be almost exact, maybe 0.5 cm room
            diff = i_meas.foot_length - u_meas.foot_length  # assuming cm

            if 0 <= diff <= 0.8:
                result = {"is_match": True, "fit_description": "True to size", "confidence": "high"}
            else:
                result = {"is_match": False, "fit_description": "Length mismatch", "confidence": "high"}

    return result


def save_userinfo(
        tool_context: ToolContext,
        user_name: str,
        user_id: str = "user_123",
) -> Dict[str, str]:
    """
    Tool to record and save username in session state.

    Args:
        tool_context: Context object providing access to session state
        user_id: Unique identifier for the user (e.g., "user_123")
        user_name: Username provided by the user.

    Returns:
        Dictionary with 'status' and 'message' keys indicating success or failure
    """
    if not hasattr(tool_context, "state"):
        return {"status": "error", "message": "Invalid ToolContext"}

    tool_context.state["user:name"] = user_name
    tool_context.state["user:userid"] = user_id

    return {
        "status": "success",
        "message": f"The user's name is saved as {user_name}"
    }


def retrieve_userinfo(tool_context: ToolContext) -> Dict[str, str]:
    """
    Tool to retrieve username from the session state.

    Args:
        tool_context: Context object providing access to the session state

    Returns:
        Dictionary with 'status' and 'user_name' keys containing the retrieved username or error message
    """
    if not hasattr(tool_context, "state"):
        return {
            "status": "error",
            "message": "Invalid ToolContext"
        }

    user_name = tool_context.state.get("user:name", "Username not found!")

    return {
        "status": "success",
        "user_name": f"The user's name is {user_name}"
    }


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)


MODEL=Gemini(
    model="gemini-2.5-flash-lite",
    retry_options=retry_config
)

wardrobe_toolset = WardrobeDBToolset(prefix="wardrobe_db_")

clothes_analysis_agent = Agent(
    name="clothes_analysis_agent",
    model=MODEL,
    description="Analyzes clothing images and extracts details for wardrobe entry.",
    instruction="""
    You are an expert at identifying clothing details from images.
    
    When given an image, extract:
    1. **Category**: trousers, shirt, dress, jacket, shoes, etc.
    2. **Brand**: Look for visible logos/tags (or say "Unknown")
    3. **Color**: Primary color (e.g., "black", "navy blue")
    4. **Estimated Size**: Based on visible tags or appearance
    5. **Condition**: Rate 1-5 based on visible wear
    6. **Notable Features**: Any patterns, style details
    
    Return as structured JSON:
    {
        "category": "shirt",
        "brand": "Zara",
        "color": "white",
        "size_tag": "M",
        "condition": 4,
        "description": "Formal button-up with collar"
    }
    
    If you can't determine something, return "Unknown" or null.
    """,
    tools=[wardrobe_toolset],
)

web_search_agent = Agent(
    name="web_search_agent",
    model=MODEL,
    description="An agent that searches the web about more details from the clothes.",
    instruction="""
    Search the web for current information about clothing brands, fit guides, or styling tips.
    You also just return in a summarized maximum of 3 sentences.
    """,
    tools=[google_search],
    sub_agents=[clothes_analysis_agent],
)

orchestrator_agent = Agent(
    name="fit_flow",
    model=MODEL,
    description="An agent responsible for communication with the user and getting best clothing recommendations.",
    instruction=ORCHESTRATOR_AGENT_INSTRUCTION,
    tools=[
        AgentTool(agent=web_search_agent),
        get_user_wardrobe,
        search_vendor_inventory,
        save_userinfo,
        retrieve_userinfo,
        get_item_details,
        calculate_fit_score,
        AgentTool(agent=clothes_analysis_agent)
    ],
)


root_agent=orchestrator_agent
