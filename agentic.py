#!/usr/bin/env python3
"""
SuperDad's T-Shirts Demo
Processes custom T-Shirt orders via two agents:
  - Agent 1 (Customization): Validates your design selections.
  - Agent 2 (Pricing): Computes a dynamic price.
Displays a live 3D preview that updates based on your chosen color, text, design style, and size.
Order IDs are auto-generated.
"""

import asyncio, random, logging
from typing import List, Dict, Any, Optional
from flask import Flask, request, render_template_string
from langchain.chains.base import Chain

logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
order_count = 0

def update_loading_bar(order_id:int, cur:int, tot:int)->None:
    percent = (cur/tot)*100
    bar = '[' + '#'*int((cur/tot)*20) + '-'*(20-int((cur/tot)*20)) + ']'
    print(f"Order {order_id}: {bar} {percent:.0f}% complete")

class TShirtOrderChain(Chain):
    @property
    def input_keys(self) -> List[str]:
        return ["order_id","customer_name","size","color","design","text"]
    @property
    def output_keys(self) -> List[str]:
        return ["estimated_cost","status"]
    async def _ainvoke(self, inputs:Dict[str,Any]) -> Dict[str,Any]:
        order = inputs.copy(); steps=2; cur=0
        logging.info(f"[LangChain] Commencing Order {order['order_id']}")
        update_loading_bar(order["order_id"], cur, steps)
        order = await self.customize_order(order); cur+=1; update_loading_bar(order["order_id"], cur, steps)
        order = await self.price_order(order); cur+=1; update_loading_bar(order["order_id"], cur, steps)
        return {"estimated_cost":order.get("estimated_cost",0.0),
                "status":order.get("status","failed")}
    async def customize_order(self,order:Dict[str,Any]) -> Dict[str,Any]:
        if order["size"].upper() not in ['S','M','L','XL']:
            raise ValueError("Invalid size. Options: S, M, L, XL.")
        if order["color"].lower() not in ['red','blue','green','black','white']:
            raise ValueError("Invalid color. Options: red, blue, green, black, white.")
        await asyncio.sleep(random.uniform(0.5,1.0))
        order["status"] = "customized"
        return order
    async def price_order(self,order:Dict[str,Any]) -> Dict[str,Any]:
        base, mult = 10.0, 1.0; 
        if order["size"].upper()=="XL": mult = 1.2
        cost_ranges = {"abstract":(4.0,6.0),"vintage":(6.0,8.0),"modern":(5.0,7.0)}
        d = order["design"].lower()
        design_cost = random.uniform(*cost_ranges[d]) if d in cost_ranges else 4.0
        t_cost = 0.05*len(order.get("text","").strip()) if order.get("text","").strip() else 0.0
        order["estimated_cost"] = (base*mult)+design_cost+t_cost
        await asyncio.sleep(random.uniform(0.3,0.7))
        order["status"] = "priced"
        return order
    def _call(self, inputs:Dict[str,Any], run_manager:Optional[Any]=None)->Dict[str,Any]:
        return asyncio.run(self._ainvoke(inputs))

app = Flask(__name__)
tshirt_chain = TShirtOrderChain()

# HTML Template
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>SuperDad's T-Shirts</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
      body { font-family:'Montserrat', sans-serif; background:#121212; color:#fff; }
      h1,h2,h3,h4,h5,h6,p,label,.form-label,.card-title,a,span { color:#fff!important; }
      .hero { background:url('https://thumbs.dreamstime.com/b/father-son-playing-superhero-sunset-time-people-having-fun-outdoors-concept-friendly-family-97721110.jpg') no-repeat center center/cover; height:60vh; display:flex; align-items:center; justify-content:center; margin-bottom:30px; position:relative; }
      .hero-overlay { position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); }
      .hero-content { position:relative; z-index:2; animation:fadeInDown 1s; text-align:center; }
      .header-title { font-size:3rem; font-weight:600; }
      .instructions, .card { background:#1e1e1e; border:none; border-radius:10px; padding:15px; margin-bottom:20px; }
      .container { max-width:600px; margin-bottom:30px; }
      .form-control, .btn, .form-select { border-radius:10px; font-weight:500; }
      .btn-primary { background-image:linear-gradient(45deg,#FDB913,#FFB347); border:none; font-weight:600; border-radius:10px; }
      .btn-primary:hover { background-image:linear-gradient(45deg,#e0a810,#FFA500); }
      footer { text-align:center; margin-top:50px; font-size:0.9em; color:#aaa; }
      #shirt-preview { width:100%; height:400px; margin-top:30px; border-radius:10px; overflow:hidden; background:#000; }
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
        <p><strong>Step 1:</strong> Enter your order details. Our agents create a custom design and compute a dynamic price.</p>
        <p><strong>Step 2:</strong> After submission, you'll see:</p>
        <ul>
          <li>A live 3D preview of the customized shirt created by our Agent(updated with your chosen color, text, design style, and size).</li>
          <li><strong>Agent 2:</strong> An explanation and the final price.</li>
        </ul>
        <p><em>Note:</em> Order IDs are auto-generated.</p>
      </div>
      {% if not result %}
      <div class="card animate__animated animate__fadeInUp">
        <h4 class="card-title mb-4">Enter Your Order Details</h4>
        <form method="POST">
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
      {% else %}
        <!-- Agent 1 Explanation -->
        <div class="card animate__animated animate__fadeInUp">
          <div class="card-body">
            <h5 class="card-title">What Our Agents Did</h5>
            <p><strong>Agent 1 (Customization):</strong> Validated your selections (size, color, design style, and custom text) to ensure they meet our requirements.</p>
          </div>
        </div>
        <!-- 3D Preview: Now placed above Agent 2 explanation -->
        <div id="shirt-preview" class="animate__animated animate__fadeInUp mt-3"></div>
        <!-- Agent 2 Explanation and Pricing -->
        <div class="card animate__animated animate__fadeInUp mt-3">
          <div class="card-body">
            <h5 class="card-title">Agent 2 (Pricing) & Final Price</h5>
            <p>Computed a dynamic price based on your selections (base price, size multiplier, design cost, and additional text cost).</p>
            <div class="alert alert-success" role="alert">
              Final price for Order {{ order.order_id }}: <strong>${{ result.estimated_cost | round(2) }}</strong>
            </div>
          </div>
        </div>
        <a href="/" class="btn btn-secondary w-100 animate__animated animate__fadeInUp mt-3">Submit Another Order</a>
      {% endif %}
    </div>
    <footer>
      <p>&copy; 2025 SuperDad's T-Shirts</p>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
      let scene, camera, renderer, shirtGroup, torso, leftSleeve, rightSleeve, designPlane;
      function getColor(name) {
        const colors = { red:0xff0000, blue:0x0000ff, green:0x008000, black:0x000000, white:0xffffff };
        return colors[name.toLowerCase()]||0xffffff;
      }
      function createDesignTexture(txt) {
        const canvas = document.createElement('canvas');
        canvas.width = 256; canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0,0,256,128);
        ctx.fillStyle = "#fff";
        ctx.font = "24px Montserrat"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText(txt,128,64);
        return new THREE.CanvasTexture(canvas);
      }
      // For Vintage design, we create an intricate T-shirt shape.
      function createVintageShape(scale) {
        const shape = new THREE.Shape();
        shape.moveTo(-2.5*scale, 1.5*scale);
        shape.lineTo(-3.0*scale, 1.5*scale);
        shape.lineTo(-3.3*scale, 0.7*scale); // left sleeve tip
        shape.lineTo(-3.3*scale, -1.5*scale);
        shape.lineTo(3.3*scale, -1.5*scale);
        shape.lineTo(3.3*scale, 0.7*scale);
        shape.lineTo(3.0*scale, 1.5*scale);
        shape.lineTo(2.5*scale, 1.5*scale);
        shape.quadraticCurveTo(0, 2.2*scale, -2.5*scale, 1.5*scale);
        shape.closePath();
        return shape;
      }
      // Initialize the shirt model based on submitted parameters.
      function initShirtModel(color, text, design, size) {
        const container = document.getElementById("shirt-preview");
        const sizeMap = { S:0.8, M:1.0, L:1.2, XL:1.4 };
        const scale = sizeMap[size.toUpperCase()]||1.0;
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(45, container.clientWidth/container.clientHeight,0.1,1000);
        renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.innerHTML = ""; container.appendChild(renderer.domElement);
        scene.add(new THREE.AmbientLight(0x404040));
        const dLight = new THREE.DirectionalLight(0xffffff,1);
        dLight.position.set(5,5,5); scene.add(dLight);
        shirtGroup = new THREE.Group();
        if(design.toLowerCase()==="vintage") {
          // Use a custom extruded shape for vintage style.
          const tshirtShape = createVintageShape(scale);
          const extrudeSettings = { depth: 0.3*scale, bevelEnabled: false, steps:1, curveSegments:32 };
          const geometry = new THREE.ExtrudeGeometry(tshirtShape, extrudeSettings);
          torso = new THREE.Mesh(geometry, new THREE.MeshPhongMaterial({color: getColor(color)}));
        } else {
          // Other designs: simple box geometry.
          torso = new THREE.Mesh(new THREE.BoxGeometry(2.5*scale, 3*scale, 0.5*scale),
                                 new THREE.MeshPhongMaterial({color: getColor(color)}));
        }
        shirtGroup.add(torso);
        // For non-vintage styles, add separate sleeves.
        if(design.toLowerCase()!=="vintage"){
          const sleeveGeom = new THREE.BoxGeometry(0.8*scale, 1.2*scale, 0.5*scale);
          const sleeveMat = new THREE.MeshPhongMaterial({color:getColor(color)});
          leftSleeve = new THREE.Mesh(sleeveGeom, sleeveMat);
          rightSleeve = new THREE.Mesh(sleeveGeom, sleeveMat);
          leftSleeve.position.set(-1.65*scale,0.7*scale,0);
          rightSleeve.position.set(1.65*scale,0.7*scale,0);
          shirtGroup.add(leftSleeve); shirtGroup.add(rightSleeve);
        }
        // Add a design plane for custom text.
        const designGeom = new THREE.PlaneGeometry(2*scale,1*scale);
        const designTex = createDesignTexture(text);
        designPlane = new THREE.Mesh(designGeom, new THREE.MeshBasicMaterial({map:designTex, transparent:true}));
        designPlane.position.set(0,0,0.26*scale);
        shirtGroup.add(designPlane);
        scene.add(shirtGroup);
        shirtGroup.rotation.y = Math.PI;
        camera.position.z = 7;
        animate();
      }
      function animate() { requestAnimationFrame(animate); shirtGroup.rotation.y += 0.005; renderer.render(scene, camera); }
      const showPreview = {{ result is not none | tojson }};
      if(showPreview) {
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

@app.route("/", methods=["GET","POST"])
def index():
    global order_count
    if request.method=="POST":
        try:
            order_count += 1
            order = {
                "order_id": order_count,
                "customer_name": request.form["customer_name"],
                "size": request.form["size"],
                "color": request.form["color"],
                "design": request.form["design"],
                "text": request.form.get("text", "")
            }
            result = tshirt_chain._call(order)
        except Exception as e:
            logging.error(f"Error processing order: {e}")
            result = {"status": "failed", "estimated_cost": 0.0}
        return render_template_string(HTML_TEMPLATE, result=result, order=order)
    next_order = order_count + 1
    return render_template_string(HTML_TEMPLATE, result=None, order={"order_id": next_order})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
