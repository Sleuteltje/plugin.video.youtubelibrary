import pafy





v = pafy.new("sdBLSTSN1HI")
print(v.title)
print(v.duration)
print(v.rating)
print(v.author)
print(v.length)
print(v.keywords)
print(v.thumb)
print(v.videoid)
print(v.viewcount)
print(v.getbest().url)
