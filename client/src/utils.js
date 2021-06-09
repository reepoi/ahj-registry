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

/**
 * Given JSON, returns new JSON with every non-array and non-object
 * field replaced with this object:
 * '<field_name>': {
 *     'Value': <field_value>
 * }
 * @param item
 * @returns {{Value}|{}|*}
 */
export function value_to_ob_value_primitive(item) {
  if (Array.isArray(item)) {
    return item.map(a => value_to_ob_value_primitive(a));
  } else if (typeof item === 'object' && item !== null) {
    return Object.keys(item).reduce((result, k) => {
      result[k] = value_to_ob_value_primitive(item[k]);
      return result;
    }, {})
  } else {
    return { Value: item }
  }
}
