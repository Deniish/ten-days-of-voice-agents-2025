
# import logging
# import json
# import os
# import asyncio
# from datetime import datetime
# from typing import Annotated, Literal
# from dataclasses import dataclass, field

# print("🚀 COFFEE SHOP AGENT")
# print("💡 agent.py LOADED SUCCESSFULLY!")


# from dotenv import load_dotenv
# from pydantic import Field
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     JobContext,
#     JobProcess,
#     RoomInputOptions,
#     WorkerOptions,
#     cli,
#     tokenize,
#     metrics,
#     MetricsCollectedEvent,
#     RunContext,
#     function_tool,
# )

# from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# logger = logging.getLogger("agent")
# load_dotenv(".env.local")

# # ======================================================
# # 🛒 ORDER MANAGEMENT SYSTEM
# # ======================================================
# @dataclass
# class OrderState:
#     """☕ Coffee shop order state with validation"""
#     drinkType: str | None = None
#     size: str | None = None
#     milk: str | None = None
#     extras: list[str] = field(default_factory=list)
#     name: str | None = None
    
#     def is_complete(self) -> bool:
#         """✅ Check if all required fields are filled"""
#         return all([
#             self.drinkType is not None,
#             self.size is not None,
#             self.milk is not None,
#             self.extras is not None,
#             self.name is not None
#         ])
    
#     def to_dict(self) -> dict:
#         """📦 Convert to dictionary for JSON serialization"""
#         return {
#             "drinkType": self.drinkType,
#             "size": self.size,
#             "milk": self.milk,
#             "extras": self.extras,
#             "name": self.name
#         }
    
#     def get_summary(self) -> str:
#         """📋 Get friendly order summary"""
#         if not self.is_complete():
#             return "🔄 Order in progress..."
        
#         extras_text = f" with {', '.join(self.extras)}" if self.extras else ""
#         return f"☕ {self.size.upper()} {self.drinkType.title()} with {self.milk.title()} milk{extras_text} for {self.name}"

# @dataclass
# class Userdata:
#     """👤 User session data"""
#     order: OrderState
#     session_start: datetime = field(default_factory=datetime.now)

# # ======================================================
# # 🛠️ BARISTA AGENT FUNCTION TOOLS
# # ======================================================

# @function_tool
# async def set_drink_type(
#     ctx: RunContext[Userdata],
#     drink: Annotated[
#         Literal["latte", "cappuccino", "americano", "espresso", "mocha", "coffee", "cold brew", "matcha"],
#         Field(description="🎯 The type of coffee drink the customer wants"),
#     ],
# ) -> str:
#     """☕ Set the drink type. Call when customer specifies which coffee they want."""
#     ctx.userdata.order.drinkType = drink
#     print(f"✅ DRINK SET: {drink.upper()}")
#     print(f"📊 Order Progress: {ctx.userdata.order.get_summary()}")
#     return f"☕ Excellent choice! One {drink} coming up!"

# @function_tool
# async def set_size(
#     ctx: RunContext[Userdata],
#     size: Annotated[
#         Literal["small", "medium", "large", "extra large"],
#         Field(description="📏 The size of the drink"),
#     ],
# ) -> str:
#     """📏 Set the size. Call when customer specifies drink size."""
#     ctx.userdata.order.size = size
#     print(f"✅ SIZE SET: {size.upper()}")
#     print(f"📊 Order Progress: {ctx.userdata.order.get_summary()}")
#     return f"📏 {size.title()} size - perfect for your {ctx.userdata.order.drinkType}!"

# @function_tool
# async def set_milk(
#     ctx: RunContext[Userdata],
#     milk: Annotated[
#         Literal["whole", "skim", "almond", "oat", "soy", "coconut", "none"],
#         Field(description="🥛 The type of milk for the drink"),
#     ],
# ) -> str:
#     """🥛 Set milk preference. Call when customer specifies milk type."""
#     ctx.userdata.order.milk = milk
#     print(f"✅ MILK SET: {milk.upper()}")
#     print(f"📊 Order Progress: {ctx.userdata.order.get_summary()}")
    
#     if milk == "none":
#         return "🥛 Got it! Black coffee - strong and simple!"
#     return f"🥛 {milk.title()} milk - great choice!"

# @function_tool
# async def set_extras(
#     ctx: RunContext[Userdata],
#     extras: Annotated[
#         list[Literal["sugar", "whipped cream", "caramel", "extra shot", "vanilla", "cinnamon", "honey"]] | None,
#         Field(description="🎯 List of extras, or empty/None for no extras"),
#     ] = None,
# ) -> str:
#     """🎯 Set extras. Call when customer specifies add-ons or says no extras."""
#     ctx.userdata.order.extras = extras if extras else []
#     print(f"✅ EXTRAS SET: {ctx.userdata.order.extras}")
#     print(f"📊 Order Progress: {ctx.userdata.order.get_summary()}")
    
#     if ctx.userdata.order.extras:
#         return f"🎯 Added {', '.join(ctx.userdata.order.extras)} - making it special!"
#     return "🎯 No extras - keeping it classic and delicious!"

# @function_tool
# async def set_name(
#     ctx: RunContext[Userdata],
#     name: Annotated[str, Field(description="👤 Customer's name for the order")],
# ) -> str:
#     """👤 Set customer name. Call when customer provides their name."""
#     ctx.userdata.order.name = name.strip().title()
#     print(f"✅ NAME SET: {ctx.userdata.order.name}")
#     print(f"📊 Order Progress: {ctx.userdata.order.get_summary()}")
#     return f"👤 Wonderful, {ctx.userdata.order.name}! Almost ready to complete your order!"

# @function_tool
# async def complete_order(ctx: RunContext[Userdata]) -> str:
#     """🎉 Finalize and save order to JSON. ONLY call when ALL fields are filled."""
#     order = ctx.userdata.order
    
#     if not order.is_complete():
#         missing = []
#         if not order.drinkType: missing.append("☕ drink type")
#         if not order.size: missing.append("📏 size")
#         if not order.milk: missing.append("🥛 milk")
#         if order.extras is None: missing.append("🎯 extras")
#         if not order.name: missing.append("👤 name")
        
#         print(f"❌ CANNOT COMPLETE - Missing: {', '.join(missing)}")
#         return f"🔄 Almost there! Just need: {', '.join(missing)}"
    
#     print(f"🎉 ORDER READY FOR COMPLETION: {order.get_summary()}")
    
#     try:
#         save_order_to_json(order)
#         extras_text = f" with {', '.join(order.extras)}" if order.extras else ""
        
#         print("\n" + "⭐" * 60)
#         print("🎉 ORDER COMPLETED SUCCESSFULLY!")
#         print(f"👤 Customer: {order.name}")
#         print(f"☕ Order: {order.size} {order.drinkType} with {order.milk} milk{extras_text}")
#         print("⭐" * 60 + "\n")
        
#         return f"""🎉 PERFECT! Your {order.size} {order.drinkType} with {order.milk} milk{extras_text} is confirmed, {order.name}! 

# ⏰ We're preparing your drink now - it'll be ready in 3-5 minutes!

# 📺 **Thanks for using our AI Barista!** 
# """
        
#     except Exception as e:
#         print(f"❌ ORDER SAVE FAILED: {e}")
#         return "⚠️ Order recorded but there was a small issue. Don't worry, we'll make your drink right away!"

# @function_tool
# async def get_order_status(ctx: RunContext[Userdata]) -> str:
#     """📊 Get current order status. Call when customer asks about their order."""
#     order = ctx.userdata.order
#     if order.is_complete():
#         return f"📊 Your order is complete! {order.get_summary()}"
    
#     progress = order.get_summary()
#     return f"📊 Order in progress: {progress}"

# class BaristaAgent(Agent):
#     def __init__(self):
#         super().__init__(
#             instructions="""
#             🏪 You are a FRIENDLY and PROFESSIONAL barista at "DASH DENISH Cafe".
            
#             🎯 MISSION: Take coffee orders by systematically collecting:
#             ☕ Drink Type: latte, cappuccino, americano, espresso, mocha, coffee, cold brew, matcha
#             📏 Size: small, medium, large, extra large
#             🥛 Milk: whole, skim, almond, oat, soy, coconut, none
#             🎯 Extras: sugar, whipped cream, caramel, extra shot, vanilla, cinnamon, honey, or none
#             👤 Customer Name: for the order
            
#             📝 PROCESS:
#             1. Greet warmly and ask for drink type
#             2. Ask for size preference  
#             3. Ask for milk choice
#             4. Ask about extras
#             5. Get customer name
#             6. Confirm and complete order
            
#             🎨 STYLE:
#             - Be warm, enthusiastic, and professional
#             - Use emojis to make it friendly
#             - Ask one question at a time
#             - Confirm choices as you go
#             - Celebrate when order is complete
            
#             🛠️ Use the function tools to record each piece of information.
#             """,
#             tools=[
#                 set_drink_type,
#                 set_size,
#                 set_milk,
#                 set_extras,
#                 set_name,
#                 complete_order,
#                 get_order_status,
#             ],
#         )

# def create_empty_order():
#     """🆕 Create a fresh order state"""
#     return OrderState()

# # ======================================================
# # 💾 ORDER STORAGE & PERSISTENCE
# # ======================================================
# def get_orders_folder():
#     """📁 Get the orders directory path"""
#     base_dir = os.path.dirname(__file__)   # src/
#     backend_dir = os.path.abspath(os.path.join(base_dir, ".."))
#     folder = os.path.join(backend_dir, "orders")
#     os.makedirs(folder, exist_ok=True)
#     return folder

# def save_order_to_json(order: OrderState) -> str:
#     """💾 Save order to JSON file with enhanced logging"""
#     print(f"\n🔄 ATTEMPTING TO SAVE ORDER...")
#     folder = get_orders_folder()
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"order_{timestamp}.json"
#     path = os.path.join(folder, filename)

#     try:
#         order_data = order.to_dict()
#         order_data["timestamp"] = datetime.now().isoformat()
#         order_data["session_id"] = f"session_{timestamp}"
        
#         with open(path, "w", encoding='utf-8') as f:
#             json.dump(order_data, f, indent=4, ensure_ascii=False)
        
#         print("\n" + "✅" * 30)
#         print("🎉 ORDER SAVED SUCCESSFULLY!")
#         print(f"📁 Location: {path}")
#         print(f"👤 Customer: {order.name}")
#         print(f"☕ Order: {order.get_summary()}")
#         print("✅" * 30 + "\n")
        
#         return path
        
#     except Exception as e:
#         print(f"\n❌ CRITICAL ERROR SAVING ORDER: {e}")
#         print(f"📁 Attempted path: {path}")
#         print("🚨 Please check directory permissions!")
#         raise e

# # ======================================================
# # 🧪 SYSTEM VALIDATION & TESTING
# # ======================================================
# def test_order_saving():
#     """🧪 Test function to verify order saving works"""
#     print("\n🧪 RUNNING ORDER SAVING TEST...")
    
#     test_order = OrderState()
#     test_order.drinkType = "latte"
#     test_order.size = "medium"
#     test_order.milk = "oat"
#     test_order.extras = ["extra shot", "vanilla"]
#     test_order.name = "TestCustomer"
    
#     try:
#         path = save_order_to_json(test_order)
#         print(f"🎯 TEST RESULT: ✅ SUCCESS - Saved to {path}")
#         return True
#     except Exception as e:
#         print(f"🎯 TEST RESULT: ❌ FAILED - {e}")
#         return False

# # ======================================================
# # 🔧 SYSTEM INITIALIZATION & PREWARMING
# # ======================================================
# def prewarm(proc: JobProcess):
#     """🔥 Preload VAD model for better performance"""
#     print("🔥 Prewarming VAD model...")
#     proc.userdata["vad"] = silero.VAD.load()
#     print("✅ VAD model loaded successfully!")

# # ======================================================
# # 🎬 AGENT SESSION MANAGEMENT
# # ======================================================
# async def entrypoint(ctx: JobContext):
#     """🎬 Main agent entrypoint - handles customer sessions"""
#     ctx.log_context_fields = {"room": ctx.room.name}

#     print("\n" + "🏪" * 25)
#     print("🚀 BREW & BEAN CAFE - AI BARISTA")
#     print("📁 Orders folder:", get_orders_folder())
#     print("🎤 Ready to take customer orders!")
#     print("🏪" * 25 + "\n")

#     # Run test to verify everything works
#     test_order_saving()

#     # Create user session data with empty order
#     userdata = Userdata(order=create_empty_order())
    
#     session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#     print(f"\n🆕 NEW CUSTOMER SESSION: {session_id}")
#     print(f"📝 Initial order state: {userdata.order.get_summary()}\n")

#     # Create session with userdata
#     session = AgentSession(
#         stt=deepgram.STT(model="nova-3"),
#         llm=google.LLM(model="gemini-2.5-flash"),
#         tts=murf.TTS(
#             voice="en-US-matthew",
#             style="Conversation",
#             text_pacing=True,
#         ),
#         turn_detection=MultilingualModel(),
#         vad=ctx.proc.userdata["vad"],
#         userdata=userdata,  # Pass userdata to session
#     )

#     # Metrics collection
#     usage_collector = metrics.UsageCollector()
#     @session.on("metrics_collected")
#     def _on_metrics(ev: MetricsCollectedEvent):
#         usage_collector.collect(ev.metrics)

#     await session.start(
#         agent=BaristaAgent(),
#         room=ctx.room,
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC()
#         ),
#     )

#     await ctx.connect()

# # ======================================================
# # ⚡ APPLICATION BOOTSTRAP & LAUNCH
# # ======================================================
# if __name__ == "__main__":
#     print("\n" + "⚡" * 25)
#     print("🎬 STARTING COFFEE SHOP AGENT...")
#     print("⚡" * 25 + "\n")
    
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))




#------------------------------ Day 3--------------------------------------


# ======================================================
# 🌿 DAILY WELLNESS VOICE COMPANION
# 💼 Professional Voice AI Agent
# 🚀 Context-Aware Wellness Assistant with JSON Persistence
# ======================================================

import logging
import json
import os
import asyncio
from datetime import datetime
from typing import Annotated
from dataclasses import dataclass, field, asdict

print("\n" + "🌿" * 50)
print("🚀 WELLNESS COMPANION INITIALIZED")
print("💡 agent.py LOADED SUCCESSFULLY!")
print("🌿" * 50 + "\n")

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    RunContext,
    function_tool,
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# 🧠 STATE MANAGEMENT & DATA STRUCTURES
# ======================================================

@dataclass
class CheckInState:
    """Holds data for the current daily wellness check-in"""
    mood: str | None = None
    energy: str | None = None
    objectives: list[str] = field(default_factory=list)
    advice_given: str | None = None
    
    def is_complete(self) -> bool:
        return all([
            self.mood is not None,
            self.energy is not None,
            len(self.objectives) > 0
        ])
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Userdata:
    """User session data passed to the agent"""
    current_checkin: CheckInState
    history_summary: str
    session_start: datetime = field(default_factory=datetime.now)

# ======================================================
# 💾 PERSISTENCE LAYER (JSON LOGGING)
# ======================================================

WELLNESS_LOG_FILE = "wellness_log.json"

def get_log_path():
    base_dir = os.path.dirname(__file__)
    backend_dir = os.path.abspath(os.path.join(base_dir, ".."))
    return os.path.join(backend_dir, WELLNESS_LOG_FILE)

def load_history() -> list:
    """Read previous check-ins from JSON"""
    path = get_log_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"⚠️ Could not load history: {e}")
        return []

def save_checkin_entry(entry: CheckInState) -> None:
    """Append new check-in to the JSON file"""
    path = get_log_path()
    history = load_history()
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "mood": entry.mood,
        "energy": entry.energy,
        "objectives": entry.objectives,
        "summary": entry.advice_given
    }
    
    history.append(record)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ CHECK-IN SAVED TO {path}")

# ======================================================
# 🛠️ WELLNESS AGENT TOOLS
# ======================================================

@function_tool
async def record_mood_and_energy(
    ctx: RunContext[Userdata],
    mood: Annotated[str, Field(description="The user's emotional state (e.g., calm, stressed, happy)")],
    energy: Annotated[str, Field(description="The user's energy level (e.g., high, low, moderate)")],
) -> str:
    """Record the user's mood and energy level"""
    ctx.userdata.current_checkin.mood = mood
    ctx.userdata.current_checkin.energy = energy
    
    print(f"📊 MOOD LOGGED: {mood} | ENERGY: {energy}")
    return f"I've noted that you're feeling {mood} with {energy} energy."

@function_tool
async def record_objectives(
    ctx: RunContext[Userdata],
    objectives: Annotated[list[str], Field(description="List of 1–3 daily goals")],
) -> str:
    """Record daily objectives"""
    ctx.userdata.current_checkin.objectives = objectives
    print(f"🎯 OBJECTIVES LOGGED: {objectives}")
    return "Your goals for today have been saved."

@function_tool
async def complete_checkin(
    ctx: RunContext[Userdata],
    final_advice_summary: Annotated[str, Field(description="A brief summary of the advice given")],
) -> str:
    """Finalize the session and save it"""
    state = ctx.userdata.current_checkin
    state.advice_given = final_advice_summary
    
    if not state.is_complete():
        return "I still need your mood, energy level, and at least one goal before завершing this session."

    save_checkin_entry(state)
    
    print("\n" + "⭐" * 60)
    print("🎉 WELLNESS CHECK-IN COMPLETED!")
    print(f"💭 Mood: {state.mood}")
    print(f"⚡ Energy: {state.energy}")
    print(f"🎯 Goals: {state.objectives}")
    print("⭐" * 60 + "\n")

    recap = f"""
Here is your wellness recap for today:
You are feeling {state.mood} and your energy is {state.energy}.
Your goals are: {', '.join(state.objectives)}.

Remember: {final_advice_summary}

Your session has been securely saved. Take care and have a mindful day!
"""
    return recap

# ======================================================
# 🤖 WELLNESS AGENT DEFINITION
# ======================================================

class WellnessAgent(Agent):
    def __init__(self, history_context: str):
        super().__init__(
            instructions=f"""
You are a compassionate, calm, and supportive Daily Wellness Companion.

Context from previous sessions:
{history_context}

🎯 **GOALS FOR THIS SESSION:**
            1. **Check-in:** Ask how they are feeling (Mood) and their energy levels.
               - *Reference the history context if available (e.g., "Last time you were tired, how is today?").*
            2. **Intentions:** Ask for 1-3 simple objectives for the day.
            3. **Support:** Offer small, grounded, NON-MEDICAL advice.
               - Example: "Try a 5-minute walk" or "Break that big task into small steps."
            4. **Recap & Save:** Summarize their mood and goals, then call 'complete_checkin'.

🚫 **SAFETY GUARDRAILS:**
            - You are NOT a doctor or therapist.
            - Do NOT diagnose conditions or prescribe treatments.
            - If a user mentions self-harm or severe crisis, gently suggest professional help immediately.

Use the provided tools to log data as the user speaks.
""",
            tools=[
                record_mood_and_energy,
                record_objectives,
                complete_checkin,
            ],
        )

# ======================================================
# 🎬 ENTRYPOINT & INITIALIZATION
# ======================================================

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n🌿 STARTING WELLNESS SESSION\n")
    
    history = load_history()
    history_summary = "No previous history found. This is your first session."
    
    if history:
        last_entry = history[-1]
        history_summary = (
            f"Your last check-in was on {last_entry.get('timestamp')}. "
            f"Mood: {last_entry.get('mood')}, Energy: {last_entry.get('energy')}. "
            f"Goals: {', '.join(last_entry.get('objectives', []))}."
        )

    userdata = Userdata(
        current_checkin=CheckInState(),
        history_summary=history_summary
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-natalie",
            style="Promo",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )
    
    await session.start(
        agent=WellnessAgent(history_context=history_summary),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))