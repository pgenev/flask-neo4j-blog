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

    def like_post(self, post_id):
        user = self.find()
        post = graph.find_one("Post", "id", post_id)
        # TODO: Check if the create_unique() method is needed
        rel = Relationship(user, "LIKES", post)
        graph.create(rel)

    def recent_posts(self, n):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT {n}
        """
        return graph.run(query, username=self.username, n=n).data()

    def similar_users(self, n):
        # TODO: Try to understand this query
        query = """
        MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user1.username = {username} AND user1 <> user2
        WITH user2, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag.name) as tag_count
        ORDER BY tag_count DESC LIMIT {n}
        RETURN user2.username AS similar_user, tags
        """
        return graph.run(query, username=self.username, n=n)

def todays_recent_posts(n):
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT {n}
    """

    today = datetime.now().strftime("%Y-%m-%d")
    return graph.run(query, today=today, n=n).data()