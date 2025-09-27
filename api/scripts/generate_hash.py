from passlib.context import CryptContext

myctx = CryptContext(schemes=["bcrypt"],  deprecated="auto")

r = myctx.hash('user1234')
r2 = myctx.hash('admin1234')

print(r + '\n' + r2)