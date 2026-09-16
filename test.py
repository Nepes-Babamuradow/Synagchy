def function_with(*                                                   ,lst:list[int]) -> None:
    lst.clear()


my_list = [1,2]

my_list=function_with(lst=my_list)
print(my_list)




from fastapi import fastAPI
app = FastAPI()

@app.get(path:"/books",summary="rusçka",tags=["kitap"])
def home():
    return "Hello world!!"


@app.get('/books')
def read_books():
    return books 

@app.get("/books")
def read_books():
    return read_books

@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
         if book['id'] == book_id:
             return 
    raise HTTPException(stats_code=404,detail="kitap yok")

class NewBook(BaseModel):
  title:str
  author:str


@app.post("/books")
def create_book(new_book:NewBook):
    books.append({
    "id":len(books) + 1,
    "title":newbook.title,
    "author":new_book.auhor,
    })


data_wo_age = {
    "email":"abc@mail.ru",
    "bio":"fenwfiewf",
    "age":12,
}


class UserSchema(BaseModel):
    email: EmailStr
    bio:str | None
    age:int = Field(ge=0,le=130)

class UserAgeSchema(UserSchema):
    age: int = Field(ge=0,le=130)


user = UserSchema(**data)
print(user)

#def func(data_: dict):
 #   data_["age"] +=1
 
class UserSchema(baseModel):
    email: EmailStr
    bio: str | None = Field(max_length=10)
    age: int = Field(ge=0,le=130)

user  UserSchema(**data_wo_age)

model_config = ConfigDict(extra='forbid')


from sqlalchemy.ext.asyncio import create_async_engine, Asyncsessionmaker


