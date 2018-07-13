require 'json'

INPUT_DIR = "/home/jball/Desktop/TweetScraper/Data/tweet"

key_to_column = Hash.new
current_row = Array.new
f = File.new('outputFile.txt','w')
f.write("'username'|'date'|'retweets'|'favorites'|'text'|'cleantext'|'is_retweet'|'ID'|'permalink'")

for filename in Dir.glob(File.join(INPUT_DIR, "*")) do
	data = JSON.parse(IO.read(filename))
		text = data["text"]
		
		text = text.gsub("http:// ","http://")
		text = text.gsub("https:// ","https://")
		text = text.gsub("http://www ","http://www")
		text = text.gsub("https://www ","https://www")
		text = text.gsub("\r","__CR__")
		text = text.gsub("\n","__NEWLINE__")
		text = text.gsub("|","__PIPE__")
	
	        textClean = text
		textClean = textClean.gsub(/pic.twitter.com\/[^\s]*/,"")
		textClean = textClean.gsub(/https:\/\/[^\s]*/,"")
		textClean = textClean.gsub(/http:\/\/[^\s]*/,"")

		data["text"] = text; 
		f.write("\n%s|%s|%d|%d|%s|%s|%s|%s|%s" % [data["usernameTweet"], data["datetime"], data["nbr_retweet"], data["nbr_favorite"], data["text"], textClean, data["is_retweet"], data["ID"], data["url"]])
end
f.close()
