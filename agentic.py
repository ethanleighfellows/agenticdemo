#!/usr/bin/env python3
"""
LangChain T-Shirt Customization and Dynamic Pricing Service with Web UI
-------------------------------------------------------------------------
This service processes T-Shirt orders in two phases:
  1. Customization: Validates and applies customer selections.
  2. Dynamic Pricing: Computes an estimated cost using configurable, dynamic factors.

Features:
- A modern, responsive web UI inspired by award-winning designs.
- An HTML form to capture all required order information.
- Asynchronous processing with randomized delays to simulate real-world dynamics.
- Detailed debug logging with contextual information.
- A dynamic progress bar printed to the console during processing.
- Integrated with LangChain's chain interface.
"""

import asyncio
import random
import logging
from typing import List, Dict, Any, Optional

from flask import Flask, request, render_template_string, redirect, url_for
from langchain.chains.base import Chain

# Configure logging for detailed output.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ----------------------------
# Utility: Progress Bar Function
# ----------------------------
def update_loading_bar(order_id: int, current_step: int, total_steps: int) -> None:
    """
    Display a dynamic text-based loading bar for the order processing.
    """
    percent = (current_step / total_steps) * 100
    bar_length = 20
    progress = int((current_step / total_steps) * bar_length)
    bar = '[' + '#' * progress + '-' * (bar_length - progress) + ']'
    print(f"Order {order_id}: {bar} {percent:.0f}% complete")

# ----------------------------
# LangChain Order Chain
# ----------------------------
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

    # Synchronous wrapper; accepts optional run_manager for compatibility.
    def _call(self, inputs: Dict[str, Any], run_manager: Optional[Any] = None) -> Dict[str, Any]:
        return asyncio.run(self._ainvoke(inputs))

# ----------------------------
# Flask Web UI Setup
# ----------------------------
app = Flask(__name__)
tshirt_chain = TShirtOrderChain()

# HTML template for the order form and results, inspired by modern design aesthetics.
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>T-Shirt Customization</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap CSS via CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background-color: #f8f9fa; font-family: 'Arial', sans-serif; }
      .container { max-width: 600px; margin-top: 50px; }
      .form-control, .btn { border-radius: 0; }
      .header { text-align: center; margin-bottom: 30px; }
      footer { text-align: center; margin-top: 50px; font-size: 0.9em; color: #666; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>T-Shirt Customization</h1>
        <p>Enter your order details below.</p>
      </div>
      {% if not result %}
      <form method="POST" action="/">
        <div class="mb-3">
          <label for="order_id" class="form-label">Order ID</label>
          <input type="number" class="form-control" name="order_id" id="order_id" required>
        </div>
        <div class="mb-3">
          <label for="customer_name" class="form-label">Customer Name</label>
          <input type="text" class="form-control" name="customer_name" id="customer_name" required>
        </div>
        <div class="mb-3">
          <label for="size" class="form-label">Size</label>
          <select class="form-select" name="size" id="size" required>
            <option value="">Choose...</option>
            <option value="S">S</option>
            <option value="M">M</option>
            <option value="L">L</option>
            <option value="XL">XL</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="color" class="form-label">Color</label>
          <select class="form-select" name="color" id="color" required>
            <option value="">Choose...</option>
            <option value="red">Red</option>
            <option value="blue">Blue</option>
            <option value="green">Green</option>
            <option value="black">Black</option>
            <option value="white">White</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="design" class="form-label">Design</label>
          <select class="form-select" name="design" id="design" required>
            <option value="">Choose...</option>
            <option value="Abstract">Abstract</option>
            <option value="Vintage">Vintage</option>
            <option value="Modern">Modern</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="text" class="form-label">Custom Text (optional)</label>
          <textarea class="form-control" name="text" id="text" rows="2"></textarea>
        </div>
        <button type="submit" class="btn btn-primary w-100">Submit Order</button>
      </form>
      {% else %}
        <div class="alert alert-{{ 'success' if result.status == 'priced' else 'danger' }}" role="alert">
          {% if result.status == 'priced' %}
            Order {{ order.order_id }} for {{ order.customer_name }} is priced at <strong>${{ result.estimated_cost | round(2) }}</strong>.
          {% else %}
            Order {{ order.order_id }} encountered an error: <strong>{{ result.status }}</strong>.
          {% endif %}
        </div>
        <a href="/" class="btn btn-secondary w-100">Submit Another Order</a>
      {% endif %}
    </div>
    <footer>
      <p>&copy; 2025 T-Shirt Customization Service</p>
    </footer>
    <!-- Bootstrap JS via CDN (optional) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Collect data from the form fields.
            order_data = {
                "order_id": int(request.form["order_id"]),
                "customer_name": request.form["customer_name"],
                "size": request.form["size"],
                "color": request.form["color"],
                "design": request.form["design"],
                "text": request.form.get("text", "")
            }
            # Run the chain synchronously via _call.
            # (Alternatively, you can use asyncio.run(tshirt_chain._ainvoke(order_data)))
            result = tshirt_chain._call(order_data)
        except Exception as e:
            logging.error(f"Error processing order from UI: {e}")
            result = {"status": "failed", "estimated_cost": 0.0}
        return render_template_string(HTML_TEMPLATE, result=result, order=order_data)
    # For GET requests, render the form.
    return render_template_string(HTML_TEMPLATE, result=None)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
