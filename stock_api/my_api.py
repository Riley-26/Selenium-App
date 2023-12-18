from flask import Flask, request, jsonify
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
import json
#C:\Users\riley\Desktop\robotics\Cyber\Personal Projects\Python\Selenium\filamentStock.py

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

filaments_json = open("filaments_dict.json")
filaments_file = json.load(filaments_json)

class Filament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.String(10), unique=False, nullable=False)
    colours = db.relationship("Colour", backref="filament", lazy=True)
    
    def __repr__(self):
        return f"{self.name}, {self.price}, {self.colours}"
    
class Colour(db.Model):
    colour_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    instock = db.Column(db.Boolean, nullable=False)
    filament_id = db.Column(db.Integer, db.ForeignKey("filament.id"), nullable=False)
    
    def __repr__(self):
        return f"{self.name}, {self.instock}"


#Routes

@app.route("/", methods=["GET"])
def index():
    filaments = Filament.query.all()
    output = []
    
    for filament in filaments:
        filament_data = {"id": filament.id, "name": filament.name, "price": filament.price}
        colours_data = []
        for colour in filament.colours:
            colours_data.append({"colour_id": colour.colour_id, "name": colour.name, "instock": colour.instock})
        filament_data["colours"] = colours_data
        output.append(filament_data)
    
    return jsonify({"filaments": output})


@app.route("/filament/<id>", methods=["GET"])
def get_filament_by_id(id):
    filament_by_id = Filament.query.get_or_404(id)
    output = []
    
    filament_data = {"id": filament_by_id.id, "name": filament_by_id.name, "price": filament_by_id.price}
    colours_data = []
    for colour in filament_by_id.colours:
        colours_data.append({"colour_id": colour.colour_id, "name": colour.name, "instock": colour.instock})
    filament_data["colours"] = colours_data
    output.append(filament_data)
    
    return jsonify({filament_by_id.name: filament_data})
    


#Create tables
# with app.app_context():
#     db.create_all()
    
#     for key, value in filaments_file.items():
#         name = key
#         price = filaments_file[key]["price"]
        
#         new_filament = Filament(name=name, price=price)
#         db.session.add(new_filament)
#         db.session.commit()
        
#         for i in value["colours"]:
#             name = i[0]
#             if i[1] == "In stock":
#                 instock = True
#             elif i[1] == "Out of stock":
#                 instock = False
#             filament = new_filament
            
#             new_filament_colour = Colour(name=name, instock=instock, filament=filament)

#             db.session.add(new_filament_colour)
#             db.session.commit()
        



if __name__ == "__main__":
    app.run(debug=True)