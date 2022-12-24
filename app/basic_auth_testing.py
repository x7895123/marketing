from basicauth import decode
encoded_str = 'Basic YXF1YWtyZzphcXVhSmtmbWc3cGRvNSE='
username, password = decode(encoded_str)
print (username, password)