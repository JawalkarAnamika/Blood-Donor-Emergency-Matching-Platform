from math import radians,sin,cos,sqrt,atan2
rules={
    "A+":["A+","A-","O+","O-"],
    "A-":["A-","O-"],
    "B+":["B+","B-","O+","O-"],
    "B-":["B-","O-"],
    "O+":["O+","O-"],
    "AB+":["A+","A-","B+","B-","AB+","AB-","O+","O-"],
    "O-":["O-"],
    "AB-":["A-","B-","AB-","O-"]
}
def compatible(donor,required):
    return donor in rules.get(required,[])
def distance(lat1,lon1,lat2,lon2):
    R=6371
    dlat=radians(lat2-lat1)
    dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2* atan2(sqrt(a),sqrt(1-a))
