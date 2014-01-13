#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

    Tree control with enhanced features and support classes.
 
"""
import wx

class TreeCtrl(wx.TreeCtrl):
    """
    
        Tree widget.
    
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE, validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style, validator, name)
    
    def MoveItemUp(self, itm, cl=None):
        """
        
            Move given item one position upwards.
            
            Parameters:
                itm    -    item (wx.TreeItem)
                cl     -    class, optional - if given, will move only within items with data of given class type
        
        """
        if itm.IsOk():
            root = self.GetItemParent(itm)
            children = self.GetItemChildren(root,cl)
            p = children.index(itm)
            if p==0:
                return False # can't move up, 1st position in the list
            allChildren = self.GetItemChildren(root) # list of all items
            p = allChildren.index(itm)
            st = self.GetItemSubTree(itm)
            self.Delete(itm)
            if p==1:
                bitm = root
            else:
                bitm = allChildren[p-2]
            nitm = self.InsertItem(root,bitm,text=st.text)
            self.CreateItemSubTree(nitm, st)
            self.SelectItem(nitm)
            return True

    def MoveItemDown(self, itm, cl=None):
        """
        
            Move given item one position downwards.
            
            Parameters:
                itm    -    item (wx.TreeItem)
                cl     -    class, optional - if given, will move only within items with data of given class type
        
        """
        if itm.IsOk():
            root = self.GetItemParent(itm)
            children = self.GetItemChildren(root)
            p = children.index(itm)
            if p==len(children)-1:
                return False # can't move down, last position in the list
            st = self.GetItemSubTree(itm)
            self.Delete(itm)
            nitm = self.InsertItem(root,children[p+1],text=st.text)
            self.CreateItemSubTree(nitm, st)
            self.SelectItem(nitm)
            return True
    
    def GetItemChildren(self, itm, cl=None):
        """
        
            Get children of given item.
            
            Parameters:
                itm    -    item (wx.TreeItem)
                cl     -    class, optional - if given, will return only items with data of given class type
            
            Output:
                item children (list)
        
        """
        children = []
        if itm.IsOk():
            child, cookie = self.GetFirstChild(itm)
            while child.IsOk():
                if cl==None:
                    children.append(child)
                    child, cookie = self.GetNextChild(itm, cookie)
                else:
                    data = self.GetItemData(child).GetData()
                    if isinstance(data,cl):
                        children.append(child)
                    child, cookie = self.GetNextChild(itm, cookie)
        return children

    def GetItemsData(self, itmlist):
        """
        
            Get data associated with items in given list.
            
            Parameters:
                itmlist    -    item list (list of wx.TreeItem)
            
            Output:
                item data list (list)
        
        """
        children = []
        if hasattr(itmlist,'__iter__'):
            for x in itmlist:
                if isinstance(x,wx.TreeItemId):
                    if x.IsOk():
                        ev = self.GetItemData(x).GetData()
                        children.append(ev)
                    else:
                        children.append([])
                else:
                    children.append([])
        return children
    
    def GetItemSubTree(self, itm, cl=None):
        """
        
            Get subtree for given item.
            
            Parameters:
                itm    -    item (wx.TreeItem)
                cl     -    class, optional - if given, will return only items with data of given class type
            
            Output:
                item subtree (SubTree)
        
        """
        if self.ItemHasChildren(itm):
            itmlist = self.GetItemChildren(itm)
            stree = SubTree(self,itm)
            for x in itmlist:
                if cl==None:
                    if self.ItemHasChildren(x):
                        st = self.GetItemSubTree(x)
                        if len(st.items)>0:
                            stree.AppendItem(st)
                        else:
                            stree.AppendItem(SubTreeItem(self,x))
                    else:
                        stree.AppendItem(SubTreeItem(self,x))
                else:
                    data = self.GetItemData(x).GetData()
                    if isinstance(data,cl):
                        if self.ItemHasChildren(x):
                            st = self.GetItemSubTree(x,cl)
                            if len(st.items)>0:
                                stree.AppendItem(st)
                            else:
                                stree.AppendItem(SubTreeItem(self,x))
                        else:
                            stree.AppendItem(SubTreeItem(self,x))
        else:
            if cl==None:
                stree = SubTreeItem(self,itm)
            else:
                data = self.GetItemData(itm).GetData()
                if isinstance(data,cl):
                    stree = SubTreeItem(self,itm)
        return stree
    
    def CreateItemSubTree(self, itm, subtree):
        """
        
            Create item subtree from given SubTree object.
            
            Parameters:
                itm        -    item (wx.TreeItem)
                subtree    -    subtree (SubTree)
        
        """
        if isinstance(itm, wx.TreeItemId):
            pass
        else:
            try:
                raise Exception()
            except:
                print "TypeError: argument 1 must be of type 'wx.TreeItemId'"
                raise
            
        if isinstance(subtree,SubTreeItem):
            if isinstance(subtree,SubTree):
                for x in subtree.items:
                    nitm = self.AppendItem(itm,x.text,x.image)
                    x.RestoreValue(nitm)
                    if isinstance(x,SubTree):
                        self.CreateItemSubTree(nitm,x)
            subtree.RestoreValue(itm)
            return True
        else:
            try:
                raise Exception()
            except:
                print "TypeError: argument 2 must be of type 'SubTree' or 'SubTreeItem'"
                raise
        return False

    def FindItem(self, data, itm = None):
        """
        
            Find item within subtree of given item (root item if none given).
            
            Parameters:
                data   -    data to be found (any)
                itm    -    item (wx.TreeItem or None)
            
            Output:
                item (wx.TreeItem)
        
        """
        if itm==None:
            itm = self.GetRootItem()
        
        if self.GetItemPyData(itm) == data:
            return itm
        else:
            if self.ItemHasChildren(itm):
                for x in self.GetItemChildren(itm):
                    v = self.FindItem(data, x)
                    if v!=None:
                        return v
            return None
        
class SubTreeItem():
    """
    
        Subtree item
    
    """
    def __init__(self, tree, itm=None):
        """
        
            Initialization.
            
            Parameters:
                tree    -    tree widget (TreeCtrl)
                itm     -    tree item (wx.TreeItem)
        
        """
        self.tree = tree
        self.text = ""
        self.font = None
        self.image = None
        self.data = None
        self.expand = False
        self.StoreValue(itm)
    
    def StoreValue(self,itm):
        """
        
            Store value of given item in subtree item object.
            
            Parameters:
                itm     -    tree item (wx.TreeItem)
        
        """
        if isinstance(itm,wx.TreeItemId):
            if itm.IsOk():
                try: # workaround for Windows with hidden root item
                    self.text = self.tree.GetItemText(itm)
                    self.font = self.tree.GetItemFont(itm)
                    self.image = self.tree.GetItemImage(itm)
                    self.data = self.tree.GetItemData(itm).GetData()
                    self.expand = self.tree.IsExpanded(itm)
                except:
                    pass
    
    def RestoreValue(self,itm):
        """
        
            Restore value of subtree item object into given item.
            
            Parameters:
                itm     -    tree item (wx.TreeItem)
        
        """
        if isinstance(itm,wx.TreeItemId):
            if itm.IsOk():
                self.tree.SetItemText(itm,self.text)
                self.tree.SetItemFont(itm,self.font)
                self.tree.SetItemImage(itm,self.image)
                self.tree.GetItemData(itm).SetData(self.data)
                if self.expand: self.tree.Expand(itm)
    
    def GetItemAttribute(self,attr):
        """
        
            Fetch value of given attribute name from stored item data.
            
            Parameters:
                attr     -    attribute name (str)
            
            Output:
                attribute value
        
        """
        if hasattr(self.data,attr):
            return getattr(self.data,attr)
        else:
            return None
    
    def IsDataInTree(self, data):
        """
        
            Check if given data is in current subtree item.
            
            Parameters:
                data     -    data (any type)
            
            Output:
                True/False
        
        """
        if self.data==data: return True
        return False

class SubTree(SubTreeItem):
    """
    
        Subtree
    
    """
    def __init__(self, tree, itm=None):
        """
        
            Initialization.
            
            Parameters:
                tree     -    tree widget (TreeCtrl)
                itm      -    tree item (wx.TreeItem)
        
        """
        SubTreeItem.__init__(self, tree, itm)
        self.items = []
    
    def AppendItem(self, item):
        """
        
            Append given item to subtree.
            
            Parameters:
                item     -    subtree (SubTree) or subtree item (SubTreeItem)
        
        """
        if isinstance(item,SubTreeItem) or isinstance(item,SubTree):
            self.items.append(item)
        else:
            try:
                raise Exception()
            except:
                print "SubTreeItemTypeError: SubTree items must be of type 'SubTree' or 'SubTreeItem'"
                raise
    
    def RemoveItem(self, pos):
        """
        
            Remove item in given position of subtree children.
            
            Parameters:
                pos     -    position (int)
        
        """
        try:
            return self.items.pop(pos)
        except IndexError:
            print "IndexError: index out of range, or sub-tree is empty"
            raise

    def InsertItem(self, pos, item):
        """
        
            Insert given item in subtree at given position.
            
            Parameters:
                item     -    subtree (SubTree) or subtree item (SubTreeItem)
                pos      -    position (int)
        
        """
        if isinstance(item,SubTreeItem) or isinstance(item,SubTree):
            try:
                self.items.insert(pos, item)
            except TypeError:
                print "TypeError: 'pos' must be an integer"
                raise
        else:
            try:
                raise Exception()
            except:
                print "SubTreeItemTypeError: SubTree items must be of type 'SubTree' or 'SubTreeItem'"
                raise

    def GetItem(self, pos):
        """
        
            Return item at given position in subtree children.
            
            Parameters:
                pos    -    position (int)
            
            Output:
                subtree (SubTree) or subtree item (SubTreeItem)
        
        """
        try:
            return self.items[pos]
        except IndexError:
            print "IndexError: index out of range, or sub-tree is empty"
            raise

    def GetDepth(self,d0=1):
        """
        
            Compute depth of subtree.
            
            Parameters:
                d0    -    initial depth (int) - used internally
            
            Output:
                depth (int)
        
        """
        d = [d0]
        for x in self.items:
            try:
                if isinstance(x,SubTree):
                    d.append(x.GetDepth(d0+1))
                else:
                    d.append(d0)
            except:
                pass
        return max(d)
    
    def GetAttributeTree(self,attr):
        """
        
            Get values of all subtree elements with given attribute.
            
            Parameters:
                attr     -    attribute name (str)
            
            Output:
                nested list of attribute values
        
        """
        tree = []
        tree.append(self.GetItemAttribute(attr))
        stree = []
        for x in self.items:
            if isinstance(x,SubTree):
                tree.append(x.GetAttributeTree(attr))
            else:
                stree.append(x.GetItemAttribute(attr))
        if len(stree)>0:
            tree.append(stree)
        return tree

    def CountOccurrences(self,attr,value):
        """
        
            Count occurrences of given attribute with given value in subtree.
            
            Parameters:
                attr     -    attribute name (str)
                value    -    value (attribute value type)
            
            Output:
                number of occurrences (int)
        
        """
        cnt = 0
        if hasattr(self.data,attr):
            if getattr(self.data,attr)==value:
                cnt += 1
        for x in self.items:
            if isinstance(x, SubTree):
                cnt += x.CountOccurrences(attr,value)
            else:
                if hasattr(x.data,attr):
                    if getattr(x.data,attr)==value:
                        cnt += 1
        return cnt

    def IsDataInTree(self, data):
        """
        
            Tell if given data is in subtree.
            
            Parameters:
                data     -    data to be searched for
            
            Output:
                True/False
        
        """
        cnt = False
        if self.data==data:
            cnt = True
        for x in self.items:
            if isinstance(x, SubTree):
                cnt = cnt or x.IsDataInTree(data)
            else:
                if x.data==data:
                    cnt = True
        return cnt
