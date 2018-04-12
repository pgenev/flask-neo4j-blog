from views import app
from models import graph

# graph.cypher.execute("CREATE CONSTRAINT ON (n:User) ASSERT n.username IS UNIQUE")
# graph.cypher.execute("CREATE CONSTRAINT ON (n:Post) ASSERT n.id IS UNIQUE")
# graph.cypher.execute("CREATE CONSTRAINT ON (n:Tag) ASSERT n.name IS UNIQUE")
# TODO: What is the idea of the INDEX ON?
graph.run("CREATE INDEX ON :Post(date)")

users = ["pgenev", "kbori"]


# TODO (1): Find a way to implement these constraints
# TODO (1) answer: Not needed. Already implemented in the database.


# TODO: Check how bcrypt/passlib works