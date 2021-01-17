export function jsonToCSV(json) {
  let csv = "";
  let flattenJSON = function(json) {
    let result = {};
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
  let keys = Array.from(
    new Set(
      Object.keys(flattenJSON(json)).map(
        objKey => objKey.substring(objKey.indexOf(".") + 1) // remove the [#]. prefix of each field
      )
    )
  );
  keys = keys.filter(key => ["Value", "Decimals", "Precision", "StartTime", "EndTime", "Unit"].includes(key.substring(key.lastIndexOf(".") + 1)));
  csv += keys.join(",") + "\n";
  for (let line of json) {
    csv +=
      keys
        .map(key =>
          key
            .split(/[\[\].]/)
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
