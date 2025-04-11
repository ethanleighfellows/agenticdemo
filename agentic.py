#!/usr/bin/env python3
"""
LangChain T-Shirt Customization and Dynamic Pricing Service
-------------------------------------------------------------
This service processes T-Shirt orders in two phases:
  1. Customization: Validates and applies customer selections.
  2. Dynamic Pricing: Computes an estimated cost using configurable, dynamic factors.

Features:
- Asynchronous processing with randomized delays to simulate real-world dynamics.
- Detailed debug logging with contextual information.
- A dynamic text-based progress bar that elegantly reflects each stage.
- Adapted for LangChain using the new ainvoke() method and updated _call signature.
"""

import asyncio
import random
import logging
from typing import List, Dict, Any, Optional
from langchain.chains.base import Chain

# Configure logging for detailed output.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def update_loading_bar(order_id: int, current_step: int, total_steps: int) -> None:
    """
    Display a dynamic text-based loading bar for the order processing.
    """
    percent = (current_step / total_steps) * 100
    bar_length = 20
    progress = int((current_step / total_steps) * bar_length)
    bar = '[' + '#' * progress + '-' * (bar_length - progress) + ']'
    print(f"Order {order_id}: {bar} {percent:.0f}% complete")

class TShirtOrderChain(Chain):
    """
    A LangChain chain that processes T-Shirt orders in two sequential steps:
    Customization and Pricing.
    """
    @property
    def input_keys(self) -> List[str]:
        return ["order_id", "customer_name", "size", "color", "design", "text"]

    @property
    def output_keys(self) -> List[str]:
        return ["estimated_cost", "status"]

    async def _ainvoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Make a copy of inputs to represent the order.
        order = inputs.copy()
        total_steps = 2
        current_step = 0
        
        logging.info(f"[LangChain] Commencing processing for Order {order['order_id']}")
        print(f"\n--- Processing Order {order['order_id']} for {order['customer_name']} ---")
        update_loading_bar(order["order_id"], current_step, total_steps)

        # Customization step.
        order = await self.customize_order(order)
        current_step += 1
        update_loading_bar(order["order_id"], current_step, total_steps)

        # Pricing step.
        order = await self.price_order(order)
        current_step += 1
        update_loading_bar(order["order_id"], current_step, total_steps)

        return {
            "estimated_cost": order.get("estimated_cost", 0.0),
            "status": order.get("status", "failed")
        }

    async def customize_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        logging.debug(f"Customization: Starting for Order {order['order_id']} with details: {order}")
        valid_sizes = ['S', 'M', 'L', 'XL']
        valid_colors = ['red', 'blue', 'green', 'black', 'white']

        if order["size"].upper() not in valid_sizes:
            logging.error(f"Customization: Invalid size '{order['size']}' for Order {order['order_id']}")
            raise ValueError(f"Invalid size '{order['size']}'. Valid options: {valid_sizes}.")
        if order["color"].lower() not in valid_colors:
            logging.error(f"Customization: Invalid color '{order['color']}' for Order {order['order_id']}")
            raise ValueError(f"Invalid color '{order['color']}'. Valid options: {valid_colors}.")

        delay = random.uniform(0.5, 1.0)
        logging.debug(f"Customization: Delay of {delay:.2f}s for Order {order['order_id']}")
        await asyncio.sleep(delay)
        order["status"] = "customized"
        logging.debug(f"Customization: Completed for Order {order['order_id']}")
        return order

    async def price_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        logging.debug(f"Pricing: Initiating computation for Order {order['order_id']}")
        base_cost = 10.0
        size_multiplier = 1.0
        if order["size"].upper() == "XL":
            size_multiplier = 1.2
            logging.debug(f"Pricing: 'XL' multiplier applied for Order {order['order_id']}")

        design_pricing_ranges = {
            "abstract": (4.0, 6.0),
            "vintage": (6.0, 8.0),
            "modern": (5.0, 7.0)
        }
        design_lower = order["design"].lower()
        if design_lower in design_pricing_ranges:
            design_cost = random.uniform(*design_pricing_ranges[design_lower])
            logging.debug(f"Pricing: Computed design cost for '{design_lower}' as ${design_cost:.2f} for Order {order['order_id']}")
        else:
            design_cost = 4.0
            logging.debug(f"Pricing: Default design cost applied for design '{order['design']}' for Order {order['order_id']}")

        text_cost = 0.0
        if order.get("text", "").strip():
            text_length = len(order["text"].strip())
            text_cost = 0.05 * text_length
            logging.debug(f"Pricing: Calculated text cost of ${text_cost:.2f} for {text_length} characters in Order {order['order_id']}")

        order["estimated_cost"] = (base_cost * size_multiplier) + design_cost + text_cost
        delay = random.uniform(0.3, 0.7)
        logging.debug(f"Pricing: Delay of {delay:.2f}s for Order {order['order_id']}")
        await asyncio.sleep(delay)
        order["status"] = "priced"
        logging.debug(f"Pricing: Final estimated cost for Order {order['order_id']} is ${order['estimated_cost']:.2f}")
        return order

    def _call(self, inputs: Dict[str, Any], run_manager: Optional[Any] = None) -> Dict[str, Any]:
        """Synchronous wrapper using asyncio.run; accepts optional run_manager for compatibility."""
        return asyncio.run(self._ainvoke(inputs))

async def main():
    # Create an instance of the TShirtOrderChain.
    tshirt_chain = TShirtOrderChain()

    # Define sample orders.
    orders = [
        {"order_id": 1, "customer_name": "Alice", "size": "M", "color": "Blue", "design": "Abstract", "text": ""},
        {"order_id": 2, "customer_name": "Bob",   "size": "XXL", "color": "Red",   "design": "Vintage",  "text": ""},  # Will trigger an error.
        {"order_id": 3, "customer_name": "Charlie", "size": "L", "color": "green", "design": "Modern", "text": "Experience the best!"}
    ]

    # Process orders concurrently.
    tasks = []
    for order in orders:
        tasks.append(asyncio.create_task(tshirt_chain.ainvoke(order)))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print("\n--- Final Order Statuses and Estimated Costs ---")
    for order, output in zip(orders, results):
        # If output is an Exception instance, mark the order as failed.
        if isinstance(output, Exception):
            logging.error(f"Error processing Order {order['order_id']}: {output}")
            print(f"Order {order['order_id']} for {order['customer_name']} - Status: failed")
        else:
            if output["status"] == "priced":
                print(f"Order {order['order_id']} for {order['customer_name']} - Estimated Cost: ${output['estimated_cost']:.2f}")
            else:
                print(f"Order {order['order_id']} for {order['customer_name']} - Status: {output['status']}")
            logging.debug(f"Final Order Data for Order {order['order_id']}: {output}")

if __name__ == "__main__":
    asyncio.run(main())
