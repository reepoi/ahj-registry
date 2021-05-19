export function jsonToCSV(json) {
  let csv = "";

  // function to flatten json to a list of fields with unique names based on position in the json
  let flattenJSON = function(json) {
    let result = {};

    // function to walk the json object
    function recurse(cur, prop) {
      if (Object(cur) !== cur) {
        result[prop] = cur;
      } else if (Array.isArray(cur)) {
        let l = cur.length;
        for (let i = 0; i < l; i++) recurse(cur[i], prop + "[" + i + "]");
        if (l === 0) result[prop] = [];
      } else {
        let isEmpty = true;
        for (let p in cur) {
          isEmpty = false;
          recurse(cur[p], prop ? prop + "." + p : p);
        }
        if (isEmpty && prop) result[prop] = {};
      }
    }
    recurse(json, "");
    return result;
  };

  // Create a unique set of column names for all included fields in the array of ahjs
  let keys = Array.from(
    new Set(
      Object.keys(flattenJSON(json)).map(
        objKey => objKey.substring(objKey.indexOf(".") + 1) // remove the [#]. prefix of each field
      )
    )
  );

  // Keep only the column names that point to primitives (no column names that point to an object)
  keys = keys.filter(key => ["Value", "Decimals", "Precision", "StartTime", "EndTime", "Unit"].includes(key.substring(key.lastIndexOf(".") + 1)));
  csv += keys.join(",") + "\n";

  // build a string representing the csv file
  for (let line of json) {
    csv +=
      keys
        .map(key =>
          key
            .split(/[[\].]/)
            .filter(i => i !== "")
            .reduce((o, i) => {
              try {
                if (o[i] === null) {
                  return "";
                }
                return o[i];
              } catch (error) {
                return "";
              }
            }, line)
        )
        .join(",") + "\n";
  }
  return csv;
}

// constructs the object that represents a room for the vue-advanced-chat
export function getRoomObject(channel,username) {
  let result = {};
  result['roomId'] = channel.ChannelID;
  result['roomName'] = channel.Users.filter(u => u.Username !== username).map(u => u.Username).join(', ');
  result['avatar'] = null; // set to Photo path?
  result['unreadCount'] = channel.NumberUnread;
  result['users'] = channel.Users.map(u => { return { _id: u.Username, username: u.Username, avatar: u.Photo }; });
  if(channel.lastMessage){
    result['lastMessage'] = getMessageObject(channel.lastMessage);
  }
  return result;
}

// constructs the object that represents a message in a chat room for the vue-advanced-chat
export function getMessageObject(pubnubMessage) {
  let result = {seen:true};
  result['content'] = pubnubMessage.message.text;
  result['senderId'] = pubnubMessage.uuid;
  result['username'] = pubnubMessage.uuid;
  result['timetoken'] = pubnubMessage.timetoken;
  return result;
}
