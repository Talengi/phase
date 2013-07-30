(function(global) {
    /**
    Object to manipulate url parameters.
    Allows to manage a string such as ?var1=value1&var2=value2 and convert it
    to an dict object, update its value, convert it back to string, or merge it.
    Usage :
    q = QueryParams();
    q.fromString("var1=value1&var2=value2")
    q.update({var2: "next value", var3: "after next value"})
    q.fromString("var4=value4")
    q.toString() // -> var1=value1&var2=next+value&var3=after+next+value&var4=value4
    q.data // -> {var1: "value1, "var2: "next value", var3: "after next value", var4: "value4"}
    */
    QueryParams = function() {
        /**
        parameters holder
        */
        this.data = {};
        this.__proto__ = {
            /**
            converts the data to a url query string
            ?param1=value1&param2=value2
            */
            toString: function toString() {
                var s = "";
                for(i in this.data) {
                    s += s ? "&":"?";
                    s += i+"="+this.data[i]
                }
                return s;
            },
            /**
            modifies a value of the data
            value: a {key: value} object or an array of {key: value} objects
            */
            update: function update(values) {
                if(values.join) {
                    for (i in values) {
                        this.update(values[i]);
                    }
                }
                for(i in values) {
                    if(values[i]) {
                        this.data[i] = values[i];
                    }
                    else {
                        delete this.data[i];
                    }
                }
                return this;
            },
            /**
            update the data from a query string
            querystring: a string formated as param1=value1&param2=value2
            */
            fromString: function fromString(querystring) {
                var params = querystring.split('&'),
                    dict = {},
                    keyValue;
                for(var i in params) {
                    keyValue = params[i].split('=');
                    dict[keyValue[0]] = keyValue[1];
                }
                this.update(dict);
                return this;
            }
        };
    };
    global.QueryParams = QueryParams;

}(window));