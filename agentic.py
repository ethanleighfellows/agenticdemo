#!/usr/bin/env python3
"""
Crew AI T-Shirt Customization and Dynamic Pricing Service
-----------------------------------------------------------
This service processes T-Shirt orders in two phases:
  1. Customization: Validates and applies customer selections.
  2. Dynamic Pricing: Computes an estimated cost using configurable, dynamic factors.
  
Features:
- Asynchronous processing with randomized delays to simulate real-world dynamics.
- Detailed debug logging with contextual information.
- A dynamic text-based progress bar that elegantly reflects each stage.
- Intricate, flexible pricing that adjusts for size, design type, and custom text length.
"""

import asyncio
import random
import logging
from dataclasses import dataclass, field
from typing import List

# Configure logging for detailed output.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@dataclass
class TShirtOrder:
    order_id: int
    customer_name: str
    size: str
    color: str
    design: str
    text: str = ""
    estimated_cost: float = field(default=0.0)
    status: str = field(default="pending")

def update_loading_bar(order_id: int, current_step: int, total_steps: int) -> None:
    """
    Display a dynamic text-based loading bar for the order processing.
    """
    percent = (current_step / total_steps) * 100
    bar_length = 20
    progress = int((current_step / total_steps) * bar_length)
    bar = '[' + '#' * progress + '-' * (bar_length - progress) + ']'
    print(f"Order {order_id}: {bar} {percent:.0f}% complete")

class Agent:
    """
    Base agent class defining the interface for order processing.
    """
    def __init__(self, name: str) -> None:
        self.name = name

    async def process(self, order: TShirtOrder) -> TShirtOrder:
        raise NotImplementedError("Subclasses should implement this method.")

class CustomizationAgent(Agent):
    """
    Validates customer options (size and color) and finalizes customization.
    """
    async def process(self, order: TShirtOrder) -> TShirtOrder:
        logging.debug(f"{self.name}: Starting customization for Order {order.order_id} | Details: {order}")
        valid_sizes = ['S', 'M', 'L', 'XL']
        valid_colors = ['red', 'blue', 'green', 'black', 'white']
        
        # Validate the options.
        if order.size.upper() not in valid_sizes:
            logging.error(f"{self.name}: Invalid size '{order.size}' for Order {order.order_id}")
            raise ValueError(f"Invalid size '{order.size}'. Valid options: {valid_sizes}.")
        if order.color.lower() not in valid_colors:
            logging.error(f"{self.name}: Invalid color '{order.color}' for Order {order.order_id}")
            raise ValueError(f"Invalid color '{order.color}'. Valid options: {valid_colors}.")

        # Simulate a dynamic processing delay.
        delay = random.uniform(0.5, 1.0)
        logging.debug(f"{self.name}: Customization delay of {delay:.2f}s for Order {order.order_id}")
        await asyncio.sleep(delay)
        
        order.status = "customized"
        logging.debug(f"{self.name}: Customization complete for Order {order.order_id}")
        return order

class PricingAgent(Agent):
    """
    Computes an estimated cost with dynamic pricing adjustments.
    """
    async def process(self, order: TShirtOrder) -> TShirtOrder:
        logging.debug(f"{self.name}: Initiating pricing computation for Order {order.order_id}")
        
        # Base cost and a size multiplier.
        base_cost = 10.0
        size_multiplier = 1.0
        if order.size.upper() == 'XL':
            size_multiplier = 1.2  # XL shirts incur a 20% premium.
            logging.debug(f"{self.name}: 'XL' size multiplier applied for Order {order.order_id}")
        
        # Dynamic design pricing: each design type has a pricing range.
        design_pricing_ranges = {
            "abstract": (4.0, 6.0),
            "vintage": (6.0, 8.0),
            "modern": (5.0, 7.0)
        }
        design_lower = order.design.lower()
        if design_lower in design_pricing_ranges:
            design_cost = random.uniform(*design_pricing_ranges[design_lower])
            logging.debug(f"{self.name}: Computed design cost for '{design_lower}' as ${design_cost:.2f} for Order {order.order_id}")
        else:
            design_cost = 4.0  # Default cost for unrecognized designs.
            logging.debug(f"{self.name}: Default design cost applied for design '{order.design}' for Order {order.order_id}")
        
        # Additional cost for custom text based on its length.
        text_cost = 0.0
        if order.text.strip():
            text_length = len(order.text.strip())
            text_cost = 0.05 * text_length  # $0.05 per character.
            logging.debug(f"{self.name}: Calculated text cost (${text_cost:.2f}) for {text_length} characters in Order {order.order_id}")
        
        # Final cost computed with dynamic adjustments.
        order.estimated_cost = (base_cost * size_multiplier) + design_cost + text_cost
        
        # Simulate a slight processing delay.
        delay = random.uniform(0.3, 0.7)
        logging.debug(f"{self.name}: Pricing delay of {delay:.2f}s for Order {order.order_id}")
        await asyncio.sleep(delay)
        
        order.status = "priced"
        logging.debug(f"{self.name}: Order {order.order_id} estimated cost finalized at ${order.estimated_cost:.2f}")
        return order

class Crew:
    """
    The Crew orchestrates the sequential processing of orders through a dynamic agent pipeline.
    """
    def __init__(self, agents: List[Agent]) -> None:
        self.agents = agents

    async def process_order(self, order: TShirtOrder) -> TShirtOrder:
        total_steps = len(self.agents)
        current_step = 0
        
        logging.info(f"[Crew] Commencing processing for Order {order.order_id}")
        print(f"\n--- Processing Order {order.order_id} for {order.customer_name} ---")
        update_loading_bar(order.order_id, current_step, total_steps)
        
        for agent in self.agents:
            try:
                order = await agent.process(order)
                current_step += 1
                update_loading_bar(order.order_id, current_step, total_steps)
            except Exception as error:
                logging.error(f"[Crew] Error in {agent.name} for Order {order.order_id}: {error}")
                order.status = "failed"
                print(f"Order {order.order_id}: Processing halted due to error: {error}")
                return order

        logging.info(f"[Crew] Processing complete for Order {order.order_id} with status '{order.status}'")
        return order

async def main():
    # Initialize the agents for customization and pricing.
    customization_agent = CustomizationAgent("CustomizationAgent")
    pricing_agent = PricingAgent("PricingAgent")
    
    # Assemble agents in the desired processing order.
    crew = Crew([customization_agent, pricing_agent])
    
    # Define sample orders with diverse input parameters.
    orders = [
        TShirtOrder(order_id=1, customer_name="Alice", size="M", color="Blue", design="Abstract"),
        TShirtOrder(order_id=2, customer_name="Bob", size="XXL", color="Red", design="Vintage"),  # Will trigger an error.
        TShirtOrder(order_id=3, customer_name="Charlie", size="L", color="green", design="Modern", text="Experience the best!")
    ]
    
    # Process all orders concurrently.
    results = await asyncio.gather(*(crew.process_order(order) for order in orders))
    
    # Output final statuses and pricing.
    print("\n--- Final Order Statuses and Estimated Costs ---")
    for order in results:
        if order.status == "priced":
            print(f"Order {order.order_id} for {order.customer_name} - Estimated Cost: ${order.estimated_cost:.2f}")
        else:
            print(f"Order {order.order_id} for {order.customer_name} - Status: {order.status}")
        logging.debug(f"Final Order Data: {order}")

if __name__ == "__main__":
    asyncio.run(main())
