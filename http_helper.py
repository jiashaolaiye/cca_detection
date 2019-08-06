from multiprocessing.dummy import Pool as ThreadPool
import requests, time

def get_access_token(name, password):

    url = 'https://passport.dding.net/login'
    headers = {
        'Accept' : 'application/json, text/plain, */*',
        'Origin' : 'https://manage.dding.net',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type' : 'application/json;charset=UTF-8',
        'Referer' : 'https://manage.dding.net'
    }
    payload = {
        'name' : name,
        'pass' : password,
        'from' : 2
    }
    response = requests.request('POST', url, headers=headers, json=payload)
    return response.cookies

def get_home_detail(keyword, cookies):
    url = ' https://manageapi.dding.net/v3/homes?offset=0&limit=10&keyword='
    url = url + keyword
    headers = {
        'Content-Type': 'Application/json',
        'User-Agent': "PostmanRuntime/7.13.0"
    }
    response = requests.request('GET', url, headers=headers, cookies=cookies)
    response = response.json()

    #解析response.json(), 返回home_id
    if 'result' in response:
        try:
            home_id = None
            home_id = response['result']['homes'][0]['id']
            home_name = response['result']['homes'][0]['home_name']
        except Exception as e:
            pass
    return home_id, home_name

def get_rooms(home_id, cookies):
    url = 'https://manageapi.dding.net/v3/homes/{}/rooms?with_device=1&with_tenant=1'.format(home_id)
    headers = {
        'Content-Type': 'Application/json',
        'User-Agent': "PostmanRuntime/7.13.0"
    }
    response = requests.request('GET', url, headers=headers, cookies=cookies)
    response = response.json()
    if 'result' in response:
        response = response['result']
    return response

def get_locks_and_gateways(rooms):
    locks = LockCollections()
    gateways = GatewayCollections()
    for room in rooms:
        if 'devices' in room:
            devices = room['devices']
            for device in devices:
                if device['device_type'] == 2:
                    lock = Lock(device, room['room_name'])
                    locks.append_lock(lock)
                if device['device_type'] == 1:
                    gateway = Gateway(device, room['room_name'])
                    gateways.append_gateway(gateway)
    return locks, gateways

class Lock:

    def __init__(self, device, room_name):
        self.device_type = device['device_type']
        self.parent_uuid = device['parent_uuid']
        self.devid = device['id']
        self.uuid = device['uuid']
        self.sn = device['sn']
        self.room_id = device['room_id']
        self.room_name = room_name
        self.exp_counts = 0
        self.lqi = 0
        self.is_cca = False

    def set_exp_counts(self, value):
        self.exp_counts = value

    def set_lqi(self, value):
        self.lqi = value

    def set_cca(self):
        self.is_cca = True


class LockCollections:

    def __init__(self):
        self.total = 0
        self.locks = []

    def append_lock(self, lock):
        self.total += 1
        self.locks.append(lock)

class Gateway:

    def __init__(self, device, room_name):
        self.device_type = device['device_type']
        self.uuid = device['uuid']
        self.room_id = device['room_id']
        self.room_name = room_name
        self.devid = device['id']
        self.exp_counts = 0

    def set_exp_counts(self, value):
        self.exp_counts = value

class GatewayCollections:

    def __init__(self):
        self.total = 0
        self.gateways = []

    def append_gateway(self, gateway):
        self.total += 1
        self.gateways.append(gateway)

def set_device_exp_counts(device, cookies):
    """
    :param device: 设备对象
    :param cookies: http请求的授权字段
    """

    headers = {
        'Content-Type': 'Application/json',
        'User-Agent': "PostmanRuntime/7.13.0"
    }
    url = 'https://manageapi.dding.net/v3/rooms/{0}/devices/{1}/exceptions?limit=20&offset=0&start_time=1561996800000&end_time=1564761599999&exception_type=1006'
    url = url.format(device.room_id, device.devid)
    response = requests.request('GET', url, headers=headers, cookies=cookies)
    response = response.json()
    if 'result' in response:
        if 'count' in response['result']:
            counts = response['result']['count']
            device.set_exp_counts(counts)

def set_lock_lqi(lock, cookies):
    """
    :param lock: 门锁对象
    :param cookies: http请求授权
    """

    headers = {
        'Content-Type': 'Application/json',
        'User-Agent': "PostmanRuntime/7.13.0"
    }
    url = 'https://manageapi.dding.net/v3/rooms/{0}/locks/{1}'
    url = url.format(lock.room_id, lock.devid)
    response = requests.request('GET', url, headers=headers, cookies=cookies)
    response = response.json()
    if 'result' in response:
        if 'lqi' in response['result']:
            lqi_value = response['result']['lqi']
            lock.set_lqi(lqi_value)

def is_cca(locks, gateways):
    for lock in locks:
        for gateway in gateways:
            if lock.parent_uuid == gateway.uuid:
                if lock.lqi > 60 and (lock.exp_counts - gateway.exp_counts) > 30:
                    lock.set_cca()

def write_data(locks, home_name):
    for lock in locks:
        with open('is_cca.txt', 'a+') as file:
            file.write('房源： '+home_name+' ')
            file.write('房间号: ' + lock.room_name+ ' ')
            file.write('门锁sn: '+ lock.sn + ' ')
            file.write('是否cca: ' + str(lock.is_cca) + '\n')


if __name__ == '__main__':
    print('开始获取cookies')
    name = '18620190127'
    password = 'ZJ07386012286'
    cookies = get_access_token(name, password)
    print('cookies获取完毕, 为：{}'.format(cookies))

    # 测试房源
    print('开始获取房源id')
    keyword = '红璞永旺店'
    home_id, home_name = get_home_detail(keyword, cookies)
    print('房源id为：{}'.format(home_id))

    # 获取房间数据
    print('开始获取房间数据')
    rooms = get_rooms(home_id, cookies)

    # 获取门锁集合和网关集合
    print('开始获取门锁和网关集合')
    locks, gateways = get_locks_and_gateways(rooms)
    print('门锁和网关集合获取完毕')


    # 设置门锁和网关对象的异常值计数
    print('开始设置门锁的异常统计值')
    p1 = ThreadPool(50)
    num = locks.total
    print('门锁总数为:{}'.format(num))
    start = time.time()
    for i in range(num):
        p1.apply_async(set_device_exp_counts, args=(locks.locks[i], cookies))
    p1.close()
    p1.join()
    print('设置门锁异常统计值共花费 %0.2f seconds' % (time.time() - start))

    print('开始设置网关的异常统计值')
    p2 = ThreadPool(50)
    num = gateways.total
    print('网关总数为:{}'.format(num))
    start = time.time()
    for i in range(num):
        p2.apply_async(set_device_exp_counts, args=(gateways.gateways[i], cookies))
    p2.close()
    p2.join()
    print('设置网关异常统计值共花费 %0.2f seconds' % (time.time() - start))

    # 设置门锁lqi值
    print('设置门锁lqi值开始')
    p3 = ThreadPool(50)
    num = locks.total
    print('门锁总数为:{}'.format(num))
    start = time.time()
    for i in range(num):
        p3.apply_async(set_lock_lqi, args=(locks.locks[i], cookies))
    p3.close()
    p3.join()
    print('设置门锁lqi值共花费 %0.2f seconds' % (time.time() - start))


    # 判定是否是cca问题
    is_cca(locks.locks, gateways.gateways)
    #输出文本
    write_data(locks.locks, home_name)
    print('done')

