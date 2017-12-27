from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
from models.item import ItemModel


class Item(Resource):
	parser = reqparse.RequestParser()
	#ensures that "price" element is passed in the json body for PUT to work
	parser.add_argument('price',
		type=float,
		required=True,
		help='This field cannot be left blank'
	)
	parser.add_argument('store_id',
		type=int,
		required=True,
		help="Every item needs a store id."
	)
	
	@jwt_required()
	def get(self,name):
		item = ItemModel.find_by_name(name)
		
		if item:
			return item.json()
		return {"message":"Item not found"}, 404 
		
	def post(self,name):
		#data variable defined after if to catch errors first. Check name if already in database to be more efficient.
		if ItemModel.find_by_name(name):
			return {'message': "An item with name '{}' already exists.".format(name)}, 400 #post failed because of user error
		
		data = Item.parser.parse_args()
		#data = request.get_json(silent=True)
		
		item = ItemModel(name,data['price'], data['store_id'])
	
		try:
			item.save_to_db()
		except:
			return {'message':'An error occurred inserting the item'}, 500  #500 = post failed because of internal servor error
			
		return item.json(), 201
		
	def delete(self,name):
		item = ItemModel.find_by_name(name)
		if item:
			item.delete_from_db()
			
		return {'message': 'Item deleted.'}
		
	def put(self,name):
		data = Item.parser.parse_args() 	#parser checks if json has requirements for input and provides the valid ones to this variable
		item = ItemModel.find_by_name(name)
		
		
		if item is None:
			item = ItemModel(name,data['price'], data['store_id'])
		else:
			item.price = data['price']
			item.store_id = data['store_id']
		item.save_to_db()
		
		return item.json()
	
	
class ItemList(Resource):
	def get(self):
		items = [item.json() for item in ItemModel.query.all()]
		return {'items': items}
		#return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}
