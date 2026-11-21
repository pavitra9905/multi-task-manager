from marshmallow import Schema, fields, validate, validates, ValidationError

STATUSES = ["todo", "in_progress", "done"]
PRIORITIES = ["low", "medium", "high"]


class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=72))

    @validates("password")
    def check_password(self, value, **kwargs):
        # bcrypt only reads the first 72 bytes
        if len(value.encode("utf-8")) > 72:
            raise ValidationError("Password is too long.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class CategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    @validates("name")
    def check_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name cannot be empty.")


class TaskSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    status = fields.Str(validate=validate.OneOf(STATUSES))
    priority = fields.Str(validate=validate.OneOf(PRIORITIES))
    due_date = fields.Date(allow_none=True)
    category_id = fields.Int(allow_none=True)

    @validates("title")
    def check_title(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Title cannot be empty.")