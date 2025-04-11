#!/usr/bin/env python3
"""
LangChain T-Shirt Customization and Dynamic Pricing Service with 3D Preview and Auto-Generated Order IDs
-----------------------------------------------------------------------------------------------------------
This demo processes custom T-Shirt orders via two agents:
  1. Customization – validates and applies your design options.
  2. Dynamic Pricing – computes a dynamic estimated cost.

The UI, branded as "SuperDad's T-Shirts," is built in high-contrast night mode with gradient gold accents,
rounded edges, and semibold Montserrat typography. The hero section displays a new background image.
After hitting "Submit Order," a live 3D preview appears, updating dynamically based on:
  - Chosen shirt color.
  - Custom text to be printed.
  - Design style (if "Vintage" is selected, a curved profile is simulated).
  - Shirt size (S, M, L, XL) affecting the model’s scale.
  
All 3D elements are built procedurally directly in the browser using Three.js.
"""

import asyncio
import random
import logging
from typing import List, Dict, Any, Optional

from flask import Flask, request, render_template_string
from langchain.chains.base import Chain

# Configure logging.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Global order counter to auto-generate Order IDs.
order_count = 0

def update_loading_bar(order_id: int, current_step: int, total_steps: int) -> None:
    """
    Displays a text-based loading bar in the terminal for the order processing.
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
      1. Customization – validates and applies your design options.
      2. Pricing – computes a dynamic estimated cost.
    """
    @property
    def input_keys(self) -> List[str]:
        return ["order_id", "customer_name", "size", "color", "design", "text"]

    @property
    def output_keys(self) -> List[str]:
        return ["estimated_cost", "status"]

    async def _ainvoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        order = inputs.copy()
        total_steps = 2
        current_step = 0

        logging.info(f"[LangChain] Commencing processing for Order {order['order_id']}")
        print(f"\n--- Processing Order {order['order_id']} for {order['customer_name']} ---")
        update_loading_bar(order["order_id"], current_step, total_steps)

        # Customization: Validate and apply design options.
        order = await self.customize_order(order)
        current_step += 1
        update_loading_bar(order["order_id"], current_step, total_steps)

        # Pricing: Compute estimated cost.
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
        return asyncio.run(self._ainvoke(inputs))

# ----------------------------
# Flask Web UI Setup
# ----------------------------
app = Flask(__name__)
tshirt_chain = TShirtOrderChain()

# HTML template with updated UI instructions and dynamic 3D preview.
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>SuperDad's T-Shirts</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
    <!-- Animate.css -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
      body {
          font-family: 'Montserrat', sans-serif;
          background-color: #121212;
          color: #fff;
      }
      h1, h2, h3, h4, h5, h6, p, label, .form-label, .card-title, a, span {
          color: #fff !important;
      }
      .hero {
          background: url('https://thumbs.dreamstime.com/b/father-son-playing-superhero-sunset-time-people-having-fun-outdoors-concept-friendly-family-97721110.jpg') no-repeat center center;
          background-size: cover;
          height: 60vh;
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          margin-bottom: 30px;
      }
      .hero-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.7);
      }
      .hero-content {
          position: relative;
          z-index: 2;
          animation: fadeInDown 1s;
      }
      .header-title {
          font-size: 3rem;
          font-weight: 600;
      }
      .instructions {
          margin-bottom: 20px;
          background: #1e1e1e;
          padding: 15px;
          border-radius: 10px;
      }
      .container {
          max-width: 600px;
          margin-bottom: 30px;
      }
      .form-control, .btn, .form-select {
          border-radius: 10px;
          font-weight: 500;
      }
      .card {
          background-color: #1e1e1e;
          border: none;
          border-radius: 10px;
      }
      .btn-primary {
          background-image: linear-gradient(45deg, #FDB913, #FFB347);
          border: none;
          font-weight: 600;
          border-radius: 10px;
      }
      .btn-primary:hover {
          background-image: linear-gradient(45deg, #e0a810, #FFA500);
      }
      footer {
          text-align: center;
          margin-top: 50px;
          font-size: 0.9em;
          color: #aaa;
      }
      /* 3D Preview container styling */
      #shirt-preview {
          width: 100%;
          height: 400px;
          margin-top: 30px;
          border-radius: 10px;
          overflow: hidden;
          background-color: #000;
      }
    </style>
  </head>
  <body>
    <div class="hero">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1 class="header-title animate__animated animate__fadeInDown">SuperDad's T-Shirts</h1>
            <p class="lead animate__animated animate__fadeInUp">Design your perfect custom t-shirt</p>
        </div>
    </div>
    <div class="container">
      <div class="instructions animate__animated animate__fadeInUp">
          <p><strong>Step 1:</strong> Enter your order details below. Our agents will validate your selections and compute a dynamic price.</p>
          <p><strong>Step 2:</strong> After submission, a live 3D preview of your shirt will appear below, updated with your chosen color, custom text, design style, and size.</p>
          <p><em>Note:</em> The order number is generated automatically.</p>
      </div>
      {% if not result %}
      <div class="card shadow-sm animate__animated animate__fadeInUp">
        <div class="card-body">
          <h4 class="card-title mb-4">Enter Your Order Details</h4>
          <form method="POST" action="/">
            <div class="mb-3">
              <label for="order_id" class="form-label">Order ID</label>
              <input type="number" class="form-control" name="order_id" id="order_id" value="{{ order.order_id }}" readonly>
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
        </div>
      </div>
      {% else %}
        <div class="alert alert-{{ 'success' if result.status == 'priced' else 'danger' }} animate__animated animate__fadeInUp" role="alert">
          {% if result.status == 'priced' %}
            Order {{ order.order_id }} for {{ order.customer_name }} is priced at <strong>${{ result.estimated_cost | round(2) }}</strong>.
          {% else %}
            Order {{ order.order_id }} encountered an error: <strong>{{ result.status }}</strong>.
          {% endif %}
        </div>
        <a href="/" class="btn btn-secondary w-100 animate__animated animate__fadeInUp">Submit Another Order</a>
      {% endif %}
      <!-- 3D Shirt Preview Section: Displayed only after a successful submission -->
      {% if result %}
      <div id="shirt-preview" class="animate__animated animate__fadeInUp"></div>
      {% endif %}
    </div>
    <footer>
      <p>&copy; 2025 SuperDad's T-Shirts</p>
    </footer>
    <!-- External JS Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
      // --- Three.js 3D Shirt Preview Implementation ---
      // Build a procedural T-shirt model and update it based on order parameters.
      let scene, camera, renderer, shirtGroup, torso, leftSleeve, rightSleeve, designPlane;

      // Function to return a hexadecimal color value based on the color name.
      function getColor(colorName) {
          const colors = {
              "red": 0xff0000,
              "blue": 0x0000ff,
              "green": 0x008000,
              "black": 0x000000,
              "white": 0xffffff
          };
          return colors[colorName.toLowerCase()] || 0xffffff;
      }

      // Create a canvas texture for custom text.
      function createDesignTexture(text) {
          const canvas = document.createElement('canvas');
          canvas.width = 256;
          canvas.height = 128;
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "#ffffff";
          ctx.font = "24px Montserrat";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(text, canvas.width / 2, canvas.height / 2);
          return new THREE.CanvasTexture(canvas);
      }

      // Initialize the shirt model with given parameters.
      function initShirtModel(orderColor, orderText, orderDesign, orderSize) {
          // Define the container here so it's always in scope.
          const container = document.getElementById("shirt-preview");

          // Set scaling factor based on size.
          const sizeMap = { "S": 0.8, "M": 1.0, "L": 1.2, "XL": 1.4 };
          const scaleFactor = sizeMap[orderSize.toUpperCase()] || 1.0;

          scene = new THREE.Scene();
          camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
          renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
          renderer.setSize(container.clientWidth, container.clientHeight);
          container.innerHTML = "";
          container.appendChild(renderer.domElement);

          // Lights.
          const ambientLight = new THREE.AmbientLight(0x404040);
          scene.add(ambientLight);
          const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
          directionalLight.position.set(5, 5, 5);
          scene.add(directionalLight);

          // Create a group for the shirt.
          shirtGroup = new THREE.Group();

          // Torso: Choose geometry based on design style.
          let torsoGeometry;
          if (orderDesign.toLowerCase() === "vintage") {
              // Vintage style: use a cylinder (curved profile).
              torsoGeometry = new THREE.CylinderGeometry(1.25 * scaleFactor, 1.25 * scaleFactor, 3 * scaleFactor, 16, 1, true);
              torsoGeometry.rotateX(Math.PI / 2);
          } else {
              // Other styles: use a box geometry.
              torsoGeometry = new THREE.BoxGeometry(2.5 * scaleFactor, 3 * scaleFactor, 0.5 * scaleFactor);
          }
          const torsoMaterial = new THREE.MeshPhongMaterial({ color: getColor(orderColor) });
          torso = new THREE.Mesh(torsoGeometry, torsoMaterial);
          shirtGroup.add(torso);

          // Sleeves: left & right.
          const sleeveGeometry = new THREE.BoxGeometry(0.8 * scaleFactor, 1.2 * scaleFactor, 0.5 * scaleFactor);
          const sleeveMaterial = new THREE.MeshPhongMaterial({ color: getColor(orderColor) });
          leftSleeve = new THREE.Mesh(sleeveGeometry, sleeveMaterial);
          rightSleeve = new THREE.Mesh(sleeveGeometry, sleeveMaterial);
          leftSleeve.position.set(-1.65 * scaleFactor, 0.7 * scaleFactor, 0);
          rightSleeve.position.set(1.65 * scaleFactor, 0.7 * scaleFactor, 0);
          shirtGroup.add(leftSleeve);
          shirtGroup.add(rightSleeve);

          // Design plane for custom text.
          const designGeometry = new THREE.PlaneGeometry(2 * scaleFactor, 1 * scaleFactor);
          const designTexture = createDesignTexture(orderText);
          const designMaterial = new THREE.MeshBasicMaterial({ map: designTexture, transparent: true });
          designPlane = new THREE.Mesh(designGeometry, designMaterial);
          designPlane.position.set(0, 0, 0.26 * scaleFactor);
          shirtGroup.add(designPlane);

          scene.add(shirtGroup);
          shirtGroup.rotation.y = Math.PI; // Initial rotation.
          camera.position.z = 7;

          animate();
      }

      function animate() {
          requestAnimationFrame(animate);
          shirtGroup.rotation.y += 0.005;
          renderer.render(scene, camera);
      }

      // Only initialize the preview if result data is available.
      const showPreview = {{ result is not none | tojson }};
      if (showPreview) {
          const orderColor = "{{ order.color | default('blue') }}";
          const orderText = "{{ order.text | default('Your Design') }}";
          const orderDesign = "{{ order.design | default('Abstract') }}";
          const orderSize = "{{ order.size | default('M') }}";
          initShirtModel(orderColor, orderText, orderDesign, orderSize);
      }
    </script>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    global order_count
    if request.method == "POST":
        try:
            order_count += 1
            order_data = {
                "order_id": order_count,
                "customer_name": request.form["customer_name"],
                "size": request.form["size"],
                "color": request.form["color"],
                "design": request.form["design"],
                "text": request.form.get("text", "")
            }
            result = tshirt_chain._call(order_data)
        except Exception as e:
            logging.error(f"Error processing order from UI: {e}")
            result = {"status": "failed", "estimated_cost": 0.0}
        return render_template_string(HTML_TEMPLATE, result=result, order=order_data)
    next_order = order_count + 1
    return render_template_string(HTML_TEMPLATE, result=None, order={"order_id": next_order})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
