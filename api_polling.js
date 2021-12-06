

const poll_rate = 3000;
let update_count = 0;

async function poll(){
    // const element = document.getElementById("energy_pv");
    // element.innerHTML = "yellow blue";
    // setTimeout(() => poll(), poll_rate);

    
    
    try {
        let response = await fetch('/all_data.php');
        let data = await response.json();
        for(let i = 0; i < data.length; i++){
            const value_el = document.getElementById(data[i][0]);
            value_el.innerHTML = data[i][1];
        }
        update_count++;
        const update_el = document.getElementById('UPDATE');
        update_el.innerHTML = 'Update count( <em><strong>' + update_count + '</strong></em> )';
    } catch (error) {
        const error_el = document.getElementById('UPDATE');
        error_el.innerHTML = '<pre id="UPDATE_ERROR" style="color: red;">Failed to reach the pi server\nTrying to connect again... again\nmake sure you computer and pi is on the network</pre>';
        console.log(error);
    }
    setTimeout(() => poll(), poll_rate);
}

poll();