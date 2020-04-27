
class BaseConfig:
	DEBUG = True
	TESTING = False
	
class ProductionConfig(BaseConfig):
	DEBUG = False 
	
class DevelopmentConfig(BaseConfig):
	DEBUG = True
	TESTING = True 
	SECRET_KEY = b'\x0b\xae\xd4\xe3\xdc\x87\xbf/Z\x18\x17\xa0\xb3\xf3\xa4\x1d'
	
