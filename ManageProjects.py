#!/usr/bin/env python
# -*-coding:utf-8 -*

# import ProjectCatalog
import json


class PhotoProject (object) :

  def __init__(self, liste) :
    self.ID   = liste[0]
    self.path = liste[1]

  def __str__(self) :
    return "ID   = %s\nPath = %s" % (self.ID, self.path)

# **********************************************************************

if __name__ == "__main__" :

  project_dict = {}

  # with open("my_dict.json", "w") as f :
  #   json.dump(
  #       project_dict, f,
  #       ensure_ascii=False,
  #       sort_keys=True,
  #       indent=2,
  #       separators=(',', ' : ')
  #   )

  cat_file = "utils/ProjectCatalog.txt"
  with open(cat_file, "r") as filein :
    project_dict = json.load(filein)

  print project_dict

# json.dump(
#   obj, fp, 
#   skipkeys=False, 
#   ensure_ascii=True, 
#   check_circular=True, 
#   allow_nan=True, 
#   cls=None, 
#   indent=None, 
#   separators=None, 
#   encoding="utf-8", 
#   default=None, 
#   sort_keys=False, 
#   **kw
# )¶
