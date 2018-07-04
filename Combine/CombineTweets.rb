require 'json'

INPUT_DIR = "/home/jball/Desktop/TweetScraper/Data/tweet"

key_to_column = Hash.new
current_row = Array.new
f = File.new('outputFile.txt','w')
#File.write('/home/jball/Desktop/outputFile.txt', 'username'|'date'|'retweets'|'favorites'|'text'|'is_retweet'|'ID'|'permalink')
f.write("'username'|'date'|'retweets'|'favorites'|'text'|'is_retweet'|'ID'|'permalink'")

for filename in Dir.glob(File.join(INPUT_DIR, "*")) do
	data = JSON.parse(IO.read(filename))
#	for t in data do
#		text = t["text"]
		text = data["text"]
=begin
		text = text.replace('http:// ','http://')
		text = text.replace('https:// ','https://')
		text = text.replace('\r','__CR__')
		text = text.replace('\n','__NEWLINE__')
		text = text.replace('|',"__PIPE__")
=end
		text = text.gsub("http:// ","http://")
		text = text.gsub("https:// ","https://")
		text = text.gsub("\r","__CR__")
		text = text.gsub("\n","__NEWLINE__")
		text = text.gsub("|","__PIPE__")
		data["text"] = text; 
#	end
#	for t in data do
#		File.write('/home/jball/Desktop/outputFile.txt', ('\n%s|%s|%d|%d|%s|%s|%s|%s|%s|%s' % (t["usernameTweet"], t["datetime"], t["nbr_retweet"], t["nbr_favorite"], t["text"], t["is_retweet"], t["ID"], t["url"])))
		f.write("\n%s|%s|%d|%d|%s|%s|%s|%s" % [ data["usernameTweet"], data["datetime"], data["nbr_retweet"], data["nbr_favorite"], data["text"], data["is_retweet"], data["ID"], data["url"] ])
#	end
end
f.close()
