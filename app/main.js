function populate_board() {
    innerhtml = ""
    for (var i=0; i<9; i++) {
        innerhtml += "<tr id=\"tr_"+i+"\">"
        for (var j=0; j<9; j++) {
            innerhtml += "<td id=\"td_"+i+"_"+j+"\"><input onkeyup=\"this.value=this.value.replace(/[^\\d]/,'')\" maxlength=\"1\" id=\"in_"+i+"_"+j+"\" type=\"text\"/></td>"
        }
        innerhtml += "</tr>"
    }
    $("#board").html(innerhtml)
}

function process_response(data) {
    if (!data["ok"]) {
        alert("Failure: "+data["msg"])
        return
    }

    rows = data["msg"].split("\n")
    for (var i=0; i<9; i++) {
        row = rows[i]
        cells = row.split(" ")
        for (var j=0; j<9; j++) {
            cell = cells[j]
            var inval = $("#in_"+i+"_"+j).val()
            classval = "immutable_given"
            if (inval == "") {
                classval = "immutable_solved" 
            }
            $("#td_"+i+"_"+j).html("<div class=\""+classval+"\">"+cell+"</div>")
        }
    }
}

function submit_board() {
    board_str = ""
    for (var i=0; i<9; i++) {
        for (var j=0; j<9; j++) {
            var inval = $("#in_"+i+"_"+j).val()
            if (inval == "") {
                inval = "."
            }
            board_str += inval + " "
        }
        board_str += "\n"
    }

    $.post('/api/', JSON.stringify({"board": board_str}), success=function (data) {
        process_response(data)
    })
}

$(document).ready(populate_board)
