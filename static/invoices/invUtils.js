function getDate(){
    let date = new Date(document.getElementById("createDate").value)
    let timezoneOffset = date.getTimezoneOffset() * 60000
    date = new Date(date.getTime() + timezoneOffset)
    console.log(1)
    // Format the date as DD MMM YYYY

    let month = date.getMonth()
    let day = date.getDate() - 1
    let year = date.getFullYear()
    let months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return `${day} ${months[month]}, ${year}`
}

function formatPrice(price){
    let dollars = `${price}`.split(".")[0]
    let cents = `${price}`.split(".")[1]
    if(cents == undefined){
        cents = "00"
    }
    if(cents.length == 1){
        cents += "0"
    }
    // Cover floating point errors
    cents = cents.slice(0,2)
    return `${dollars}.${cents}`
}

function updateAddressFromDropdown(){

    let box_text = document.getElementById("addrDropdown").value

    if(box_text == "New Address"){
        document.getElementById("RA1").value = ""
        document.getElementById("RA1").disabled = false
        document.getElementById("RA2").value = ""
        document.getElementById("RA2").disabled = false
        document.getElementById("RA3").value = ""
        document.getElementById("RA3").disabled = false
        document.getElementById("RA4").value = ""
        document.getElementById("RA4").disabled = false
        return;
    } else {
        document.getElementById("RA1").disabled = true
        document.getElementById("RA2").disabled = true
        document.getElementById("RA3").disabled = true
        document.getElementById("RA4").disabled = true
    }

    addresses.forEach( elt => {
        if(elt.desc == box_text){
            document.getElementById("RA1").value = elt.addr1
            document.getElementById("RA2").value = elt.addr2
            document.getElementById("RA3").value = elt.addr3
            document.getElementById("RA4").value = elt.addr4
        }
    
    })
}
function updateIfSGA(){
    let status = getCurrentStatus()
    let recordType = getCurrentType()

    if(recordType == "SGA Budget Request"){
        document.getElementById("addrDropdown").value = "SGA Budget"
        updateAddressFromDropdown()
        document.getElementById("addrDropdown").disabled = true
    } else{
        document.getElementById("addrDropdown").value = "New Address"
        updateAddressFromDropdown()
        document.getElementById("addrDropdown").disabled = false
    }

    if(recordType == "SGA Budget Request" && status == "Granted"){
        let approverBox = document.getElementById("approver")
        approverBox.value = "SGA Finance Board"
        approverBox.disabled = true
    }

    if(recordType != "SGA Budget Request" && status == "Pending"){
        let approverBox = document.getElementById("approver")
        approverBox.disabled = false
    } else if (recordType == "SGA Budget Request" && status == "Pending"){
        let approverBox = document.getElementById("approver")
        approverBox.disabled = true
    }
}

function getCurrentStatus(){
    let status = null
    document.getElementsByName("statusSelect").forEach((elt) => {
        if(elt.checked){
            status = elt.id
        }
    })
    return status
}

function getCurrentType(){
    let recordType = null
    document.getElementsByName("types").forEach((elt) => {
        if(elt.checked){
            recordType = elt.id;
        }
    })
    return recordType
}

function preview(){

    if(getDate() == "NaN undefined, NaN"){
        alert("Please enter a valid date")
        return
    }

    let post_data = {
        "id": document.getElementById("ID").value,
        "date": getDate(),
        "creator": document.getElementById("creator").value,
        "approver": document.getElementById("approver").value,
        "return_addr": [
            document.getElementById("RA1").value,
            document.getElementById("RA2").value,
            document.getElementById("RA3").value,
            document.getElementById("RA4").value],
        "li": [
            
        ],
        "type": getCurrentType(),
        "tax": formatPrice(document.getElementById("taxes").value),
        "fees": formatPrice(document.getElementById("fees").value),
        "total": formatPrice(document.getElementById("total").value),
        "status": getCurrentStatus()
    }

    let table = document.getElementById("products")
    for(let i = 1; i < table.rows.length - 1; i++){

        console.log(`prod${i}`)
        let item = {
            "line": i,
            "desc": document.getElementById(`prod${i}`).value,
            "ammt": formatPrice(document.getElementById(`price${i}`).value),
            "qty": document.getElementById(`qty${i}`).value,
            "total": formatPrice(document.getElementById(`price${i}`).value * document.getElementById(`qty${i}`).value)
        }
        post_data.li.push(item)
    }
    let xhr = new XMLHttpRequest()
    xhr.open("POST", "/invoices/preview")
    xhr.setRequestHeader("Content-Type", "application/json")
    xhr.send(JSON.stringify(post_data))
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4){
            if(xhr.status == 200){
                let win = window.open("", "Preview", "width=800,height=600")
                win.document.write(xhr.responseText)
            } else{
                alert("Error Previewing Record")
            }
        }
    }
}
function removeRow(rowID){
    let table = document.getElementById("products")
    table.deleteRow(rowID)

    // Go through the table and update the line IDs
    for(let i = rowID; i < table.rows.length; i++){
        table.rows[i].cells[0].innerText = i
        table.rows[i].cells[4].innerHTML = `<button onClick="removeRow(${i})">x</button>`
    }
}

class Address{
    constructor(desc, addr1, addr2, addr3, addr4){
        this.desc = desc
        this.addr1 = addr1
        this.addr2 = addr2
        this.addr3 = addr3
        this.addr4 = addr4
    }
}