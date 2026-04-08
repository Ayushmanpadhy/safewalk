const mysql = require('mysql2/promise');
const fs = require('fs');

async function dump() {
    const pool = mysql.createPool({
        host: 'localhost',
        user: 'root',
        password: 'root123',
        database: 'safewalk',
    });

    try {
        const [rows] = await pool.query('SELECT * FROM street_safety_scores');
        const features = [];
        for (let r of rows) {
            if (r.geometry) {
                let geom = typeof r.geometry === 'string' ? JSON.parse(r.geometry) : r.geometry;
                features.push({
                    type: "Feature",
                    properties: {
                        street_name: r.street_name,
                        street_id: r.street_id,
                        score: r.score,
                        score_day: r.score_day,
                        score_night: r.score_night,
                        active_report_count: r.active_report_count,
                        trend: r.trend,
                        escalated: r.escalated
                    },
                    geometry: {
                        type: "LineString",
                        coordinates: geom
                    }
                });
            }
        }
        const geojson = { type: "FeatureCollection", features };
        fs.writeFileSync('d:/SAFEWALK/sw-final/js/indian_roads.js', 'const ALL_ROADS_DATA = ' + JSON.stringify(geojson) + ';\n');
        console.log('Dumped ' + features.length + ' rows cleanly to indian_roads.js!');
    } catch (e) {
        console.error(e);
    }
    process.exit(0);
}

dump();
