# Nextmap Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 ph03n1x
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Adds a !nextmap function to B3 for Call of Duty servers even though it is not a built-in RCON command.

__version__ = '1.0.0'
__author__ = 'ph03n1x'

import b3, time, threading, re
import b3.events
import b3.plugin

from b3.functions import getCmd

class NextmapPlugin(b3.plugin.Plugin):
    _mapChanged = False
    _mapRequested = ""
    _allMaps = {"ambush": "mp_convoy",
         "backlot": "mp_backlot",
         "bloc": "mp_bloc",
         "bog": "mp_bog",
         "broadcast": "mp_broadcast",
         "chinatown": "mp_carentan",
         "countdown": "mp_countdown",
         "crash": "mp_crash",
         "creek": "mp_creek",
         "crossfire": "mp_crossfire",
         "district": "mp_citystreets",
         "downpour": "mp_farm",
         "killhouse": "mp_killhouse",
         "overgrown": "mp_overgrown",
         "pipeline": "mp_pipeline",
         "shipment": "mp_shipment",
         "showdown": "mp_showdown",
         "strike": "mp_strike",
         "vacant": "mp_vacant",
         "wet work": "mp_cargoship",
        }


    def onStartup(self):
        #Get admin plugin
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False

        # Register commands
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

        #Register events
        self.registerEvent('EVT_GAME_EXIT', self.onGameEnd)

    def onLoadConfig(self):
        q = self.config.get('settings', 'custom_maps')
        if not q:
            self.debug('No custom maps defined in config. Using only stock maps')
            return
        q1 = q.split(',')
        for entry in q1:
            q2 = []
            q2 = entry.split('-')
            self._allMaps[q2[0]] = q2[1]
            self.debug('Added %s:%s to available maps.' % (q2[0], self._allMaps[q2[0]]))
        

    def onGameEnd(self, event):
        """
        Handle EVT_GAME_ROUND_END
        """
        if self._mapChanged:
            self.confirmMap()
                
    def confirmMap(self):
        self.console.write('map %s' % self._allMaps[self._mapRequested])
        self._mapChanged = False


    def _search(self, maplist, partial):
        a = []
        for k in maplist:
            if partial in k:
                a.append(k)
        return a

    def aquireCmdLock2(self, cmd, client, delay, all=True):
        if client.maxLevel >= 20:
            return True
        elif cmd.time + 5 <= self.console.time():
            return True
        else:
            return False


    #----------------------- COMMANDS ---------------------------------

    def cmd_setnextmap(self, data, client=None, cmd=None):
        """\
        <mapname> - Set the nextmap (partial map name works)
        """
        if not data:
            client.message('^7Invalid or missing data, try !help setnextmap')
            return
        match = self._search(self._allMaps, data)
        if len(match) == 1:
            self._mapRequested = match[0]
            self._mapChanged = True
            if client:
                client.message('^7Next map set to ^2%s^7' % self._mapRequested.title())
        elif len(match) > 1:
            match = (', ').join(match)
            client.message('Available matches: %s' % match)
        elif len(match) == 0:
            client.message('No maps matching your request')
            
        
    def cmd_nextmap(self, data, client=None, cmd=None):
        """\
        - list the next map in rotation
        """
        if not self.aquireCmdLock2(cmd, client, 60, True):
            client.message('^7Do not spam commands')
            return

        if self._mapChanged:
            cmd.sayLoudOrPM(client, '^7Next Map: ^2%s' % self._mapRequested.title())
            return
                
        mapname = self.console.getNextMap()
        if mapname:
            cmd.sayLoudOrPM(client, '^7Next Map: ^2%s' % mapname)
        else:
            client.message('^1Error:^7 could not get map list')


    def cmd_allmaps(self, data, client=None, cmd=None):
        """\
        - Shows a list of all available maps
        """
        all = self._allMaps
        all = (', ').join(all.keys()).title()
        cmd.sayLoudOrPM(client, 'Available Maps: ^2%s' % all)


    def cmd_cyclemap(self, data, client=None, cmd=None):
        """\
        Cycle to next map in rotation
        """
        if self._mapChanged:
            self.confirmMap()
        else:
            self.console.rotateMap()
            
##    # This will correct maprotate in the event it is used.
##    def cmd_maprotate(self, data, client, cmd=None):
##        """\
##        Cycle to next map in rotation
##        """
##        if self._mapChanged:
##            self.confirmMap()
##        else:
##            self.console.rotateMap()
            
        

        
