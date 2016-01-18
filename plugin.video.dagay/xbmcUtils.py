import sys
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

class xbmcUtils(object):
    #######################################
    # Xbmc Helpers
    #######################################
    def __init__(self, pluginhandle=None):
        self.handle = int(sys.argv[1])
        if pluginhandle is not None:
            self.handle = pluginhandle

    def select(self, title, menuItems):
        select = xbmcgui.Dialog().select(title, menuItems)
        if select == -1:
            return None
        else:
            return menuItems[select]

    def getKeyboard(self, default='', heading='', hidden=False):
        kboard = xbmc.Keyboard(default, heading, hidden)
        kboard.doModal()
        if kboard.isConfirmed():
            return kboard.getText()
        return ''

    def getImage(self, title):
        dialog = xbmcgui.Dialog()
        image = dialog.browse(1, title, 'pictures', '.jpg|.png', True)
        return image

    def showMessage(self, msg):
        xbmc.executebuiltin('Notification(SportsDevil,' + str(msg.encode('utf-8', 'ignore')) + ')')

    def showBusyAnimation(self):
        xbmc.executebuiltin('ActivateWindow(busydialog)')

    def hideBusyAnimation(self):
        xbmc.executebuiltin('Dialog.Close(busydialog,true)')

    def closeAllDialogs(self):
        xbmc.executebuiltin('Dialog.Close(all, true)')

    def log(self, msg):
        try:
            xbmc.log(msg)
        except:
            xbmc.log(msg.encode('utf-8'))

    def addSortMethod(self, method):
        xbmcplugin.addSortMethod(handle=self.handle, sortMethod=method)

    def setSortMethodsForCurrentXBMCList(self, sortKeys):
        if not sortKeys or sortKeys == []:
            self.addSortMethod(xbmcplugin.SORT_METHOD_UNSORTED)
        else:
            if 'name' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_LABEL)
            if 'size' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_SIZE)
            if 'duration' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_DURATION)
            if 'genre' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_GENRE)
            if 'rating' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_VIDEO_RATING)
            if 'date' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_DATE)
            if 'file' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_FILE)
            if 'none' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_UNSORTED)

    def getContainerFolderPath(self):
        return xbmc.getInfoLabel('Container.FolderPath')

    def getListItemPath(self):
        return xbmc.getInfoLabel('ListItem.Path')

    def getCurrentWindow(self):
        return xbmc.getInfoLabel('System.CurrentWindow')

    def getCurrentControl(self):
        return xbmc.getInfoLabel('System.CurrentControl')

    def getCurrentWindowXmlFile(self):
        return xbmc.getInfoLabel('Window.Property(xmlfile)')
