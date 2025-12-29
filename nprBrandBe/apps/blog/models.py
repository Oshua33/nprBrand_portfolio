import edgy
from nprOlusolaBe.apps.label.models import Label
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.lib.database.base_model import BaseModel
from nprOlusolaBe.apps.account.models import User


class BlogCategory(BaseModel):
    name: str = edgy.CharField(max_length=100)


class BlogTag(BaseModel):
    name: str = edgy.CharField(max_length=100)


class Blog(BaseModel):
    title: str = edgy.CharField(max_length=100)
    description: str = edgy.TextField()
    image: Media = edgy.ForeignKey(Media, on_delete=edgy.SET_NULL, null=True)
    is_publish: bool = edgy.BooleanField(default=True)
    category: BlogCategory | None = edgy.ForeignKey("BlogCategory", null=True)
    label: Label | None = edgy.ForeignKey(Label, null=True)
    # tags: list[BlogTag] | None = edgy.ManyToMany("BlogTag", related_name="tags")


class BlogLike(BaseModel):
    author: User = edgy.ForeignKey("User", on_delete=edgy.CASCADE, related_name="likes")
    blog: Blog = edgy.ForeignKey("Blog", on_delete=edgy.CASCADE, related_name="likes")


class BlogComment(BaseModel):
    user: User = edgy.ForeignKey(
        "User", on_delete=edgy.CASCADE, related_name="comments"
    )
    blog: Blog = edgy.ForeignKey(
        "Blog", on_delete=edgy.CASCADE, related_name="comments"
    )
    comment: str = edgy.TextField()
