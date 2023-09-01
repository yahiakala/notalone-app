import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q


# def role_check(user, permissions):
#     "Validate that a users role(s) have all the required permissions"
#     perm_dict = {}
#     for perm in permissions:
#         for role in user['roles']:
#             if role[perm] == True:
#                 perm_dict[perm] = True
#     print(perm_dict, len(perm_dict), len(permissions))
#     return len(perm_dict) == len(permissions)


# def perm_to_roles(permissions, all=True):
#     perm_dict = {perm: True}
#     app_tables.roles.search(
#         tenant=user['tenant'],
#         q.all_of(
#             **perm_dict
#         )
#     )