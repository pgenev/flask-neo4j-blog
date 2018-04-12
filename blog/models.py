from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid

graphURL='http://localhost:7474/db/data/'
graphUser = "neo4j"
graphPassphrase = "neegolf4"

graph=Graph(graphURL, user=graphUser, password=graphPassphrase)
# graph.delete_all()


class User:

    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        return False

    def verify_password(self, password):
        user = self.find()
        if not user:
            return False
        return bcrypt.verify(password, user["password"])

    def add_post(self, title, tags, text):
        user = self.find()

        post = Node(
            "Post",
            id=str(uuid.uuid4()).capitalize(),
            title=title,
            text=text,
            timestamp=int(datetime.now().strftime("%s")),
            date=datetime.now().strftime("%Y-%m-%d")
        )

        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(",")]
        tags = set(tags)

        # TODO: Find a way to implement the code below. merge_one is not working this way. (DONE)
        for tag in tags:
            t = Node("Tag", name=tag)
            # t = graph.merge_one("Tag", "name", tag)
            graph.merge(t)
            rel = Relationship(t, "TAGGED", post)
            graph.create(rel)

def todays_recent_posts(n):
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT {n}
    """

    today = datetime.now().strftime("%Y-%m-%d")
    return graph.run(query, today=today, n=n)