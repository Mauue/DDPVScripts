const i2_topology = [
    ["Chicago", "New_York"],
    ["Chicago", "Kansas"],
    ["Chicago", "Washington"],
    ["Houston", "Los_Angeles"],
    ["Kansas", "Salt_Lake_City"],
    ["Chicago", "Atlanta"],
    ["Seattle", "Salt_Lake_City"],
    ["Houston", "Kansas"],
    ["Seattle", "Los_Angeles"],
    ["Salt_Lake_City", "Los_Angeles"],
    ["New_York", "Washington"],
    ["Atlanta", "Washington"],
    ["Atlanta", "Houston"]
];

const yidongyun_topology = [
    ["BM", "A"],
    ["A", "SW"],
    ["B", "SW"],
    ["VM", "B"],
    ["SW", "Aggr"],
    ["Aggr", "C"],
    ["C", "BMGW"],
];

const network1_topology = [
    ["S", "A"],
    ["A", "B"],
    ["B", "C"],
    ["C", "D"],
    ["A", "W"],
    ["B", "W"],
    ["C", "W"],
    ["D", "W"],
]

const topology_options =  {
    title: {
        text: 'Topology'
    },
    // animationDurationUpdate: 1500,
    // animationEasingUpdate: 'quinticInOut',
    series: [
        {
            type: 'graph',
            layout: 'force',
            symbolSize: 50,
            roam: true,
            force: {
                repulsion: 500,
                edgeLength: [50, 100],
                gravity: 0,
                initLayout: 'circular',
                // layoutAnimation: false,
            },
            label: {
                show: true,
                // color: '#000',
                fontWeight: 800,
            },
            symbol:'rect',
            itemStyle:{borderWidth:0, color:'rgb(250,230,153)',},
            // edgeSymbol: ['circle', 'arrow'],
            // edgeSymbolSize: [4, 10],
            edgeLabel: {
                fontSize: 20
            },
            data: [],
            // links: [],
            links: [],
            lineStyle: {
                color: 'rgb(0,0,0)',
                width: 5,
                curveness: 0
            },
            textStyle:{

                fontSize: 16,
            },

        }
    ]
};

const DVNet_options =  {
    title: {
        text: 'DVNet',
        subtext: 'DVNet is a DAG compactly representing all paths in the network\nthat satisfies the requirement.',
        subtextStyle: {
            fontSize: 16,
            // fontWeight: 'bold',
        }
    },
    legend:{
        show: true,
        selectedMode: false
    },
    animationDurationUpdate: 0,
    animationEasingUpdate: 'quinticInOut',
    stateAnimation: {
        duration: 2500,
        // easing
    },
    series: [
        {
            type: 'graph',
            layout: 'force',
            symbolSize: 50,
            roam: true,
            force: {
                repulsion: 500,
                edgeLength: [50, 100],
                gravity: 0,
                initLayout: 'circular',
                friction: 0.8,
            },
            label: {
                show: true,
                // color: '#000',
                fontWeight: 800,
            },
            // zoom:2,
            categories:[{
                name:"Destination",
                itemStyle:{borderWidth:0, color: 'rgb(107,230,293)'},
            },{
                name:"Common",
                itemStyle:{borderWidth:0, color: 'rgb(63,177,227)'},
            },{
                name:"Source",
                itemStyle:{borderWidth:0, color: 'rgb(98,108,145)'},
            }],
            // itemStyle:{borderWidth:3, borderColor:'black', color: 'rgb(189,215,238)'},
            edgeSymbol: ['none', 'arrow'],
            // edgeSymbolSize: [4, 10],
            edgeLabel: {
                fontSize: 20
            },
            data: [],
            // links: [],
            links: [],
            lineStyle: {
                color:'rgb(0,0,0)',
                width: 5,
                opacity: 1,
            },
            textStyle:{
                fontSize: 16,
            },

        }
    ]
};
