class FilterModule(object):

    def filters(self):
        return {
            'find_peer': self.find_peer,
        }

    def find_peer(self, my_location, peering):
        result = []
        for peer in peering:
            if peer['left'] == my_location:
                pass
            elif peer['right'] == my_location:
                peer['right'] = peer['left']
            else:
                continue
            peer.pop('left')
            peer['name'] = peer.pop('right')
            result.append(peer)
        return result
