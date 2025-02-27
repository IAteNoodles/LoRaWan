import simpy
class Channel:
    def __init__(self, env, channelFrequency, channelID, capacity=1):
        self.env = env
        self.frequency = channelFrequency
        self.channelID = channelID
        self.resource = simpy.Resource(env, capacity=capacity)
        self.store = simpy.Store(env)

    def request_channel(self):
        return self.resource.request()

    def transmit(self, packet):
        yield self.store.put(packet)
        print(f"{self.env.now}: Channel {self.channelID} transmitted packet with signal :{packet}")

    def receive(self):
        packet = yield self.store.get()
        return packet
    
    def is_busy(self):
        return self.resource.count > 0