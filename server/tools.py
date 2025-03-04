###############################
##  TOOLS
from langchain.agents import Tool
from langchain.tools import BaseTool
from langchain.tools import StructuredTool
from datetime import date, datetime
import json
import re
import os


def get_current_user(input : str):
    db = TransactionDb()
    user = db.get_user(1)
    db.close()
    return user

get_current_user_tool = Tool(
    name='GetCurrentUser',
    func= get_current_user,
    description="Returns the current user for querying transactions."
)

def get_transactions(userId : str):
    """Returns the transactions associated to the userId provided by running this query: SELECT * FROM Transactions WHERE userId = ?."""
    try:
        db = TransactionDb()
        transactions = db.get_user_transactions(userId)
        db.close()
        return transactions
        
    except Exception as e:
        return f"Error: {e}'"
            

get_recent_transactions_tool = Tool(
    name='GetUserTransactions',
    func= get_transactions,
    description="Returns the transactions associated to the userId provided by running this query: SELECT * FROM Transactions WHERE userId = provided_userId."
)


################### Agent tools definition #########################
import os
str_docs_dir_path = "_docs"


def list_documents(param: str):
    global str_docs_dir_path
    docnames = []
    try:
        items = os.listdir(str_docs_dir_path)
        docnames = [item for item in items if os.path.isfile(str_docs_dir_path + "\\" + item) and item.endswith(".txt")]
    except:
        pass
    return docnames

list_documents_tool = Tool(
    name="ListDocuments",
    func=list_documents,
    description="""Lists all documents."""
)
list_documents_structtool = StructuredTool.from_function(
    name="ListDocuments",
    func=list_documents,
    description="""Lists all documents."""
)

def get_document_contents(docname: str):
    global str_docs_dir_path
    ret = ""
    try:
        ret = open(str_docs_dir_path + "\\" + docname, "r").read()
    except:
        ret = "An error occured loading contents of the document."
    return ret

get_document_contents_tool = Tool(
    name="GetDocumentContents",
    func=get_document_contents,
    description="""Returns contents of a .txt file with name 'docname'"""
)
get_document_contents_structtool = StructuredTool.from_function(
    name="GetDocumentContents",
    func=get_document_contents,
    description="""Returns contents of a .txt file with name 'docname'"""
)

def save_message(msg: str):
    try:
        msg_json = {
            "time": datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
            "message": msg
        }
        open("saved_messages\\saved_messages.txt", "a").write(
            json.dumps(msg_json, indent = "\t")
        )
    except:
        pass

save_message_tool = Tool(
    name="SaveMessage",
    func=save_message,
    description="""Write message 'msg'"""
)
save_message_structtool = StructuredTool.from_function(
    name="SaveMessage",
    func=save_message,
    description="""Write message 'msg'"""
)
