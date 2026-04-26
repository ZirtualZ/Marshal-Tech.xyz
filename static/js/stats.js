const cpuChart = new Chart(document.getElementById("cpuChart"), {
    type: "line",
    data: {
        labels: Array(60).fill(""),
                           datasets: [{
                               label: "CPU %",
                               data: [],
                               borderColor: "#4c6ef5",
                               backgroundColor: "rgba(76,110,245,0.15)",
                           fill: true,
                           tension: 0.4,
                           pointRadius: 0
                           }]
    },
    options: {
        responsive: true,
        animation: false,
        scales: {
            y: { beginAtZero: true, max: 100 },
            x: { display: false }
        }
    }
});


const netChart = new Chart(document.getElementById("netChart"), {
    type: "line",
    data: {
        labels: Array(60).fill(""),
                           datasets: [
                               {
                                   label: "Upload",
                                   data: [],
                                   borderColor: "#e64980",
                                   tension: 0.4,
                                   pointRadius: 0
                               },
                               {
                                   label: "Download",
                                   data: [],
                                   borderColor: "#2f9e44",
                                   tension: 0.4,
                                   pointRadius: 0
                               }
                           ]
    },
    options: {
        responsive: true,
        animation: false,
        scales: {
            y: { beginAtZero: true },
            x: { display: false }
        }
    }
});


let upHistory = [];
let dlHistory = [];


async function updateStats() {

    try {

        const res = await fetch("/api/stats");
        const d = await res.json();


        /* ---------- Top Stats ---------- */

        document.getElementById("system").innerText = d.system.hostname;

        document.getElementById("cpu").innerText =
        `${d.cpu_total.toFixed(1)}%`;

        document.getElementById("ram").innerText =
        `${d.ram.used} / ${d.ram.total} GB (${d.ram.pct}%)`;

        document.getElementById("uptime").innerText =
        d.uptime;

        document.getElementById("temp").innerText =
        `${d.temperature.toFixed(1)}°C`;


        /* ---------- CPU Chart ---------- */

        cpuChart.data.datasets[0].data = d.cpu_history;
        cpuChart.update();


        /* ---------- Network Chart ---------- */

        upHistory.push(d.network.up);
        dlHistory.push(d.network.dl);

        if (upHistory.length > 60) {
            upHistory.shift();
            dlHistory.shift();
        }

        netChart.data.datasets[0].data = upHistory;
        netChart.data.datasets[1].data = dlHistory;

        netChart.update();


        /* ---------- Disks ---------- */

        const disks = document.getElementById("disks");

        const filtered = d.disks.filter(disk => {

            const m = disk.mount;

            /* remove snap mounts */
            if (m.startsWith("/snap")) return false;

            /* remove system bind mounts */
            if (["/etc","/tmp","/usr","/var/tmp"].includes(m)) return false;

            /* remove weird snapd paths */
            if (m.includes("snapd")) return false;

            return true;

        });

        disks.innerHTML = filtered.map(disk => `
        <div class="disk">
        ${disk.mount} — ${disk.percent.toFixed(1)}%
        <div class="disk-bar">
        <div class="disk-inner" style="width:${disk.percent}%"></div>
        </div>
        </div>
        `).join("");

    } catch(e) {
        console.error("Stats update failed:", e);
    }

}

setInterval(updateStats, 2000);
updateStats();
