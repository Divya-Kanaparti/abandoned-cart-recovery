// // // import { useEffect, useState } from 'react';
// // // import {
// // //   ResponsiveContainer,
// // //   BarChart,
// // //   Bar,
// // //   XAxis,
// // //   YAxis,
// // //   Tooltip,
// // //   PieChart,
// // //   Pie,
// // //   Cell
// // // } from 'recharts';

// // // import {
// // //   ShoppingCart,
// // //   Users,
// // //   Mail,
// // //   IndianRupee,
// // //   ShieldCheck,
// // //   AlertTriangle,
// // //   RefreshCw,
// // //   LayoutDashboard,
// // //   Package,
// // //   Send,
// // //   ChartNoAxesCombined
// // // } from 'lucide-react';

// // // const API = 'http://127.0.0.1:8000/api';

// // // export default function App() {
// // //   const [data, setData] = useState({});
// // //   const [tab, setTab] = useState('Overview');
// // //   const [rows, setRows] = useState([]);
// // //   const [err, setErr] = useState('');
// // //   const [loading, setLoading] = useState(false);
// // //   // Consent management filters
// // // const [consentSearch, setConsentSearch] = useState('');
// // // const [consentChannel, setConsentChannel] = useState('ALL');
// // // const [consentStatus, setConsentStatus] = useState('ALL');

// // //   // Load dashboard data
// // //   const load = async () => {
// // //     try {
// // //       setErr('');

// // //       const response = await fetch(API + '/dashboard');

// // //       if (!response.ok) {
// // //         throw new Error(await response.text());
// // //       }

// // //       setData(await response.json());
// // //     } catch (error) {
// // //       setErr(error.message || 'API unavailable');
// // //     }
// // //   };

// // //   // Load records for the selected tab
// // //   const loadRows = async (selectedTab) => {
// // //     const endpoints = {
// // //     Customers: '/customers',
// // //     Carts: '/carts',
// // //     Campaigns: '/campaigns',
// // //     'Send History': '/sends',
// // //     Orders: '/orders?limit=500',
// // //     // Anomalies: '/anomalies',
// // //     // 'Consent Management': '/consents?limit=1000',
// // //     'Audit Decisions': '/audit-decisions?limit=500',
// // //     'Consent Management': '/consents?limit=1000'
// // //   };
// // //     // const endpoints = {
// // //     //   Customers: '/customers',
// // //     //   Carts: '/carts',
// // //     //   Campaigns: '/campaigns',
// // //     //   'Send History': '/sends',
// // //     //   Orders: '/orders?limit=500',
// // //     //   Anomalies: '/anomalies',
// // //     //   'Audit Decisions': '/audit-decisions?limit=500'
// // //     // };

// // //     if (!endpoints[selectedTab]) {
// // //       setRows([]);
// // //       return;
// // //     }

// // //     try {
// // //       setLoading(true);

// // //       const response = await fetch(API + endpoints[selectedTab]);

// // //       if (!response.ok) {
// // //         throw new Error('Unable to fetch records');
// // //       }

// // //       const result = await response.json();
// // //       setRows(Array.isArray(result) ? result : []);
// // //     } catch {
// // //       setRows([]);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   // Initial dashboard loading
// // //   useEffect(() => {
// // //     load();
// // //   }, []);

// // //   // Load records whenever the selected tab changes
// // //   useEffect(() => {
// // //     loadRows(tab);
// // //   }, [tab]);

// // //   // Navigation items
// // //   const nav = [
// // //     ['Overview', LayoutDashboard],
// // //     ['Customers', Users],
// // //     ['Carts', ShoppingCart],
// // //     ['Campaigns', Send],
// // //     ['Send History', Mail],
// // //     ['Orders', Package],
// // //     ['Anomalies', AlertTriangle],
// // //     // ['Audit Decisions', ShieldCheck]
// // //     ['Audit Decisions', ShieldCheck],
// // //     ['Consent Management', ShieldCheck]
// // //   ];

// // //   // Dashboard metrics
// // //   const metrics = [
// // //     ['Customers', data.customers, Users],
// // //     ['Total carts', data.carts, ShoppingCart],
// // //     ['Abandoned', data.abandoned_carts, AlertTriangle],
// // //     ['Recovered', data.recovered_carts, RefreshCw],
// // //     ['Messages delivered', data.messages_delivered, Mail],
// // //     ['Orders', data.orders, Package],
// // //     ['Attributed orders', data.attributed_orders, ChartNoAxesCombined],
// // //     [
// // //       'Recovered revenue',
// // //       `₹${(data.recovered_revenue || 0).toLocaleString('en-IN')}`,
// // //       IndianRupee
// // //     ]
// // //   ];

// // //   // Messaging funnel data
// // //   const chart = [
// // //     {
// // //       name: 'Attempted',
// // //       value: data.messages_attempted || 0
// // //     },
// // //     {
// // //       name: 'Delivered',
// // //       value: data.messages_delivered || 0
// // //     },
// // //     {
// // //       name: 'Opened',
// // //       value: data.messages_opened || 0
// // //     },
// // //     {
// // //       name: 'Clicked',
// // //       value: data.messages_clicked || 0
// // //     }
// // //   ];

// // //   // Refresh dashboard and current table
// // //   const refreshData = () => {
// // //     load();

// // //     if (tab !== 'Overview') {
// // //       loadRows(tab);
// // //     }
// // //   };

// // //   // Display values safely
// // //   const displayValue = (value) => {
// // //     return value == null ? '—' : String(value);
// // //   };

// // //   // Format table column names
// // //   const formatColumn = (key) => {
// // //     return key.replace(/_/g, ' ');
// // //   };
// // //   // Consent management summary and filtering
// // // const consentOptedIn = rows.filter(
// // //   row => row.status === 'OPTED_IN'
// // // ).length;

// // // const consentOptedOut = rows.filter(
// // //   row => row.status === 'OPTED_OUT'
// // // ).length;

// // // const filteredConsentRows = rows.filter(row => {
// // //   const search = consentSearch.toLowerCase();

// // //   const matchesSearch =
// // //     String(row.customer_name || '').toLowerCase().includes(search) ||
// // //     String(row.customer_id || '').toLowerCase().includes(search);

// // //   const matchesChannel =
// // //     consentChannel === 'ALL' || row.channel === consentChannel;

// // //   const matchesStatus =
// // //     consentStatus === 'ALL' || row.status === consentStatus;

// // //   return matchesSearch && matchesChannel && matchesStatus;
// // // });

// // //   return (
// // //     <div className="shell">

// // //       {/* SIDEBAR */}
// // //       <aside>
// // //         <div className="brand">
// // //           <div className="brandicon">
// // //             CR
// // //           </div>

// // //           <div>
// // //             <b>CartRecover</b>
// // //             <small>COMMERCE INTELLIGENCE</small>
// // //           </div>
// // //         </div>

// // //         <div className="navlabel">
// // //           WORKSPACE
// // //         </div>

// // //         {nav.map(([name, Icon]) => (
// // //           <button
// // //             className={tab === name ? 'active' : ''}
// // //             onClick={() => setTab(name)}
// // //             key={name}
// // //           >
// // //             <Icon size={18} />
// // //             {name}
// // //           </button>
// // //         ))}

// // //         <div className="sidebottom">
// // //           <ShieldCheck size={18} />

// // //           Consent-first orchestration

// // //           <small>
// // //             MySQL · Local environment
// // //           </small>
// // //         </div>
// // //       </aside>

// // //       {/* MAIN CONTENT */}
// // //       <main>

// // //         {/* HEADER */}
// // //         <header>
// // //           <div>
// // //             <span className="eyebrow">
// // //               OPERATIONS / {tab.toUpperCase()}
// // //             </span>

// // //             <h1>
// // //               {tab === 'Overview' ? 'Recovery overview' : tab}
// // //             </h1>

// // //             <p>
// // //               Monitor recovery performance, customer permissions and conversion outcomes.
// // //             </p>
// // //           </div>

// // //           <button
// // //             className="refresh"
// // //             onClick={refreshData}
// // //           >
// // //             <RefreshCw size={16} />
// // //             Refresh data
// // //           </button>
// // //         </header>

// // //         {/* ERROR MESSAGE */}
// // //         {err && (
// // //           <div className="error">
// // //             <AlertTriangle size={18} />

// // //             <div>
// // //               <b>Backend connection unavailable</b>
// // //               <br />
// // //               {err}
// // //               <br />
// // //               Start MySQL, load the starter dataset, then run FastAPI.
// // //             </div>
// // //           </div>
// // //         )}

// // //         {/* OVERVIEW DASHBOARD */}
// // //         {tab === 'Overview' ? (
// // //           <>
// // //             {/* METRIC CARDS */}
// // //             <section className="metrics">
// // //               {metrics.map(([name, value, Icon]) => (
// // //                 <div className="metric" key={name}>
// // //                   <div className="metrichead">
// // //                     <span>{name}</span>
// // //                     <Icon size={18} />
// // //                   </div>

// // //                   <strong>
// // //                     {value ?? 0}
// // //                   </strong>

// // //                   <small>
// // //                     Live database metric
// // //                   </small>
// // //                 </div>
// // //               ))}
// // //             </section>

// // //             {/* CHARTS */}
// // //             <section className="charts">

// // //               {/* MESSAGING FUNNEL */}
// // //               <div className="panel">
// // //                 <div className="paneltitle">
// // //                   <div>
// // //                     <b>Messaging funnel</b>
// // //                     <small>
// // //                       Communication event progression
// // //                     </small>
// // //                   </div>

// // //                   <span className="pill">
// // //                     ALL CHANNELS
// // //                   </span>
// // //                 </div>

// // //                 <ResponsiveContainer width="100%" height={260}>
// // //                   <BarChart data={chart}>
// // //                     <XAxis dataKey="name" />
// // //                     <YAxis />
// // //                     <Tooltip />

// // //                     <Bar
// // //                       dataKey="value"
// // //                       fill="#5367e8"
// // //                       radius={[6, 6, 0, 0]}
// // //                     />
// // //                   </BarChart>
// // //                 </ResponsiveContainer>
// // //               </div>

// // //               {/* CART LIFECYCLE */}
// // //               <div className="panel">
// // //                 <div className="paneltitle">
// // //                   <div>
// // //                     <b>Cart lifecycle</b>
// // //                     <small>
// // //                       Current cart distribution
// // //                     </small>
// // //                   </div>
// // //                 </div>

// // //                 <ResponsiveContainer width="100%" height={260}>
// // //                   <PieChart>
// // //                     <Pie
// // //                       data={[
// // //                         {
// // //                           name: 'Abandoned',
// // //                           value: data.abandoned_carts || 0
// // //                         },
// // //                         {
// // //                           name: 'Active',
// // //                           value: data.active_carts || 0
// // //                         },
// // //                         {
// // //                           name: 'Recovered',
// // //                           value: data.recovered_carts || 0
// // //                         }
// // //                       ]}
// // //                       dataKey="value"
// // //                       nameKey="name"
// // //                       innerRadius={62}
// // //                       outerRadius={92}
// // //                       paddingAngle={4}
// // //                     >
// // //                       {[0, 1, 2].map(index => (
// // //                         <Cell
// // //                           key={index}
// // //                           fill={['#5367e8', '#19a88b', '#f2a64b'][index]}
// // //                         />
// // //                       ))}
// // //                     </Pie>

// // //                     <Tooltip />
// // //                   </PieChart>
// // //                 </ResponsiveContainer>
// // //               </div>
// // //             </section>

// // //             {/* BUSINESS RULES */}
// // //             <section className="panel insight">
// // //               <div>
// // //                 <b>
// // //                   <ShieldCheck size={18} />
// // //                   Consent and suppression guardrails
// // //                 </b>

// // //                 <p>
// // //                   Messages are eligible only when the latest effective
// // //                   channel consent is OPTED_IN. Unknown and withdrawn
// // //                   consent is suppressed.
// // //                 </p>
// // //               </div>

// // //               <div>
// // //                 <b>
// // //                   <ChartNoAxesCombined size={18} />
// // //                   Attribution policy
// // //                 </b>

// // //                 <p>
// // //                   Single-touch, 7-day attribution. A qualifying click
// // //                   outranks open and delivery; one order receives at
// // //                   most one campaign credit.
// // //                 </p>
// // //               </div>
// // //             </section>
// // //           </>
// // //         ) : (
// // //           /* DATA TABLES */
// // //           <section className="panel tablepanel">
// // //             <div className="paneltitle">
// // //               <div>
// // //                 <b>{tab}</b>
// // //                 <small>
// // //                   Records from the MySQL database
// // //                 </small>
// // //               </div>

// // //               <span className="pill">
// // //                 {rows.length} RECORDS
// // //               </span>
// // //             </div>

// // //             {loading ? (
// // //               <div className="empty">
// // //                 Loading records...
// // //               </div>
// // //             ) : rows.length === 0 ? (
// // //               <div className="empty">
// // //                 No records available. Check the database connection and load the dataset.
// // //               </div>
// // //             ) : (
// // //               <div className="tablewrap">

// // //                 {/* SPECIAL ORDERS TABLE */}
// // //                 {tab === 'Orders' ? (
// // //                   <table>
// // //                     <thead>
// // //                       <tr>
// // //                         <th>Order ID</th>
// // //                         <th>Customer ID</th>
// // //                         <th>Order Total</th>
// // //                         <th>Ordered At</th>
// // //                         <th>Attribution Status</th>
// // //                         <th>Attribution ID</th>
// // //                         <th>Campaign ID</th>
// // //                         <th>Send ID</th>
// // //                         <th>Attributed Revenue</th>
// // //                       </tr>
// // //                     </thead>

// // //                     <tbody>
// // //                       {rows.map((row, index) => {
// // //                         const attributed = row.attribution_id != null;

// // //                         return (
// // //                           <tr key={index}>
// // //                             <td>{displayValue(row.order_id)}</td>
// // //                             <td>{displayValue(row.customer_id)}</td>
// // //                             <td>
// // //                               ₹{Number(row.order_total || 0).toLocaleString('en-IN')}
// // //                             </td>
// // //                             <td>{displayValue(row.ordered_at)}</td>
// // //                             <td>
// // //                               {attributed ? 'Attributed' : 'Not Attributed'}
// // //                             </td>
// // //                             <td>
// // //                               {row.attribution_id ?? 'Not Attributed'}
// // //                             </td>
// // //                             <td>
// // //                               {row.attributed_campaign_id ?? 'Not Attributed'}
// // //                             </td>
// // //                             <td>
// // //                               {row.attributed_send_id ?? 'Not Attributed'}
// // //                             </td>
// // //                             <td>
// // //                               {attributed
// // //                                 ? `₹${Number(row.attributed_revenue || 0).toLocaleString('en-IN')}`
// // //                                 : '—'}
// // //                             </td>
// // //                           </tr>
// // //                         );
// // //                       })}
// // //                     </tbody>
// // //                   </table>

// // //                 ) : tab === 'Audit Decisions' ? (
// // //                   /* SPECIAL AUDIT DECISIONS TABLE */
// // //                   <table>
// // //                     <thead>
// // //                       <tr>
// // //                         <th>Decision ID</th>
// // //                         <th>Customer ID</th>
// // //                         <th>Cart ID</th>
// // //                         <th>Channel</th>
// // //                         <th>Decision</th>
// // //                         <th>Reason Code</th>
// // //                         <th>Explanation</th>
// // //                         <th>Decided At</th>
// // //                       </tr>
// // //                     </thead>

// // //                     <tbody>
// // //                       {rows.map((row, index) => (
// // //                         <tr key={index}>
// // //                           <td>{displayValue(row.decision_id)}</td>
// // //                           <td>{displayValue(row.customer_id)}</td>
// // //                           <td>{displayValue(row.cart_id)}</td>
// // //                           <td>{displayValue(row.channel)}</td>
// // //                           <td>{displayValue(row.decision)}</td>
// // //                           <td>{displayValue(row.reason_code)}</td>
// // //                           <td>{displayValue(row.detail)}</td>
// // //                           <td>{displayValue(row.decided_at)}</td>
// // //                         </tr>
// // //                       ))}
// // //                     </tbody>
// // //                   </table>

// // //                 ) : (
// // //                   /* DEFAULT TABLE FOR OTHER TABS */
// // //                   <table>
// // //                     <thead>
// // //                       <tr>
// // //                         {Object.keys(rows[0]).slice(0, 8).map(key => (
// // //                           <th key={key}>
// // //                             {formatColumn(key)}
// // //                           </th>
// // //                         ))}
// // //                       </tr>
// // //                     </thead>

// // //                     <tbody>
// // //                       {rows.map((row, index) => (
// // //                         <tr key={index}>
// // //                           {Object.keys(row).slice(0, 8).map(key => (
// // //                             <td key={key}>
// // //                               {displayValue(row[key])}
// // //                             </td>
// // //                           ))}
// // //                         </tr>
// // //                       ))}
// // //                     </tbody>
// // //                   </table>
// // //                 )}
// // //               </div>
// // //             )}
// // //           </section>
// // //         )}

// // //         {/* FOOTER */}
// // //         <footer>
// // //           <span>
// // //             CartRecover · Abandoned Cart Recovery Platform
// // //           </span>

// // //           <span>
// // //             DEMO DATA · NO LIVE MESSAGES SENT
// // //           </span>
// // //         </footer>
// // //       </main>
// // //     </div>
// // //   );
// // // }


// // import { useEffect, useState } from 'react';

// // import {
// //   ResponsiveContainer,
// //   BarChart,
// //   Bar,
// //   XAxis,
// //   YAxis,
// //   Tooltip,
// //   PieChart,
// //   Pie,
// //   Cell
// // } from 'recharts';

// // import {
// //   ShoppingCart,
// //   Users,
// //   Mail,
// //   IndianRupee,
// //   ShieldCheck,
// //   AlertTriangle,
// //   RefreshCw,
// //   LayoutDashboard,
// //   Package,
// //   Send,
// //   ChartNoAxesCombined
// // } from 'lucide-react';

// // const API = 'http://127.0.0.1:8000/api';

// // export default function App() {
// //   const [data, setData] = useState({});
// //   const [tab, setTab] = useState('Overview');
// //   const [rows, setRows] = useState([]);
// //   const [err, setErr] = useState('');
// //   const [loading, setLoading] = useState(false);
// //   // Consent management filters
// // const [consentSearch, setConsentSearch] = useState('');
// // const [consentChannel, setConsentChannel] = useState('ALL');
// // const [consentStatus, setConsentStatus] = useState('ALL');

// //   // Load dashboard data
// //   const load = async () => {
// //     try {
// //       setErr('');

// //       const response = await fetch(API + '/dashboard');

// //       if (!response.ok) {
// //         throw new Error(await response.text());
// //       }

// //       setData(await response.json());
// //     } catch (error) {
// //       setErr(error.message || 'API unavailable');
// //     }
// //   };

// //   // Load records for the selected tab
// //   const loadRows = async (selectedTab) => {
// //     const endpoints = {
// //       Customers: '/customers',
// //       Carts: '/carts',
// //       Campaigns: '/campaigns',
// //       'Send History': '/sends',
// //       Orders: '/orders?limit=500',
// //       Anomalies: '/anomalies',
// //       'Audit Decisions': '/audit-decisions?limit=500',
// //       'Consent Management': '/consents?limit=1000'
// //     };

// //     if (!endpoints[selectedTab]) {
// //       setRows([]);
// //       return;
// //     }

// //     try {
// //       setLoading(true);

// //       const response = await fetch(API + endpoints[selectedTab]);

// //       if (!response.ok) {
// //         throw new Error('Unable to fetch records');
// //       }

// //       const result = await response.json();
// //       setRows(Array.isArray(result) ? result : []);
// //     } catch {
// //       setRows([]);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   // Initial dashboard loading
// //   useEffect(() => {
// //     load();
// //   }, []);

// //   // Load records whenever the selected tab changes
// //   useEffect(() => {
// //     loadRows(tab);
// //   }, [tab]);

// //   // Navigation items
// //   const nav = [
// //     ['Overview', LayoutDashboard],
// //     ['Customers', Users],
// //     ['Carts', ShoppingCart],
// //     ['Campaigns', Send],
// //     ['Send History', Mail],
// //     ['Orders', Package],
// //     ['Anomalies', AlertTriangle],
// //     // ['Audit Decisions', ShieldCheck]
// //     ['Audit Decisions', ShieldCheck],
// //     ['Consent Management', ShieldCheck]
// //   ];

// //   // Dashboard metrics
// //   const metrics = [
// //     ['Customers', data.customers, Users],
// //     ['Total carts', data.carts, ShoppingCart],
// //     ['Abandoned', data.abandoned_carts, AlertTriangle],
// //     ['Recovered', data.recovered_carts, RefreshCw],
// //     ['Messages delivered', data.messages_delivered, Mail],
// //     ['Orders', data.orders, Package],
// //     ['Attributed orders', data.attributed_orders, ChartNoAxesCombined],
// //     [
// //       'Recovered revenue',
// //       `₹${(data.recovered_revenue || 0).toLocaleString('en-IN')}`,
// //       IndianRupee
// //     ]
// //   ];

// //   // Messaging funnel data
// //   const chart = [
// //     {
// //       name: 'Attempted',
// //       value: data.messages_attempted || 0
// //     },
// //     {
// //       name: 'Delivered',
// //       value: data.messages_delivered || 0
// //     },
// //     {
// //       name: 'Opened',
// //       value: data.messages_opened || 0
// //     },
// //     {
// //       name: 'Clicked',
// //       value: data.messages_clicked || 0
// //     }
// //   ];

// //   // Refresh dashboard and current table
// //   const refreshData = () => {
// //     load();

// //     if (tab !== 'Overview') {
// //       loadRows(tab);
// //     }
// //   };

// //   // Display values safely
// //   const displayValue = (value) => {
// //     return value == null ? '—' : String(value);
// //   };

// //   // Format table column names
// //   const formatColumn = (key) => {
// //     return key.replace(/_/g, ' ');
// //   };
// //   // Consent management summary and filtering
// // const consentOptedIn = rows.filter(
// //   row => row.status === 'OPTED_IN'
// // ).length;

// // const consentOptedOut = rows.filter(
// //   row => row.status === 'OPTED_OUT'
// // ).length;

// // const filteredConsentRows = rows.filter(row => {
// //   const search = consentSearch.toLowerCase();

// //   const matchesSearch =
// //     String(row.customer_name || '').toLowerCase().includes(search) ||
// //     String(row.customer_id || '').toLowerCase().includes(search);

// //   const matchesChannel =
// //     consentChannel === 'ALL' || row.channel === consentChannel;

// //   const matchesStatus =
// //     consentStatus === 'ALL' || row.status === consentStatus;

// //   return matchesSearch && matchesChannel && matchesStatus;
// // });

// //   return (
// //     <div className="shell">

// //       {/* SIDEBAR */}
// //       <aside>
// //         <div className="brand">
// //           <div className="brandicon">
// //             CR
// //           </div>

// //           <div>
// //             <b>CartRecover</b>
// //             <small>COMMERCE INTELLIGENCE</small>
// //           </div>
// //         </div>

// //         <div className="navlabel">
// //           WORKSPACE
// //         </div>

// //         {nav.map(([name, Icon]) => (
// //           <button
// //             className={tab === name ? 'active' : ''}
// //             onClick={() => setTab(name)}
// //             key={name}
// //           >
// //             <Icon size={18} />
// //             {name}
// //           </button>
// //         ))}

// //         <div className="sidebottom">
// //           <ShieldCheck size={18} />

// //           Consent-first orchestration

// //           <small>
// //             MySQL · Local environment
// //           </small>
// //         </div>
// //       </aside>

// //       {/* MAIN CONTENT */}
// //       <main>

// //         {/* HEADER */}
// //         <header>
// //           <div>
// //             <span className="eyebrow">
// //               OPERATIONS / {tab.toUpperCase()}
// //             </span>

// //             <h1>
// //               {tab === 'Overview' ? 'Recovery overview' : tab}
// //             </h1>

// //             <p>
// //               Monitor recovery performance, customer permissions and conversion outcomes.
// //             </p>
// //           </div>

// //           <button
// //             className="refresh"
// //             onClick={refreshData}
// //           >
// //             <RefreshCw size={16} />
// //             Refresh data
// //           </button>
// //         </header>

// //         {/* ERROR MESSAGE */}
// //         {err && (
// //           <div className="error">
// //             <AlertTriangle size={18} />

// //             <div>
// //               <b>Backend connection unavailable</b>
// //               <br />
// //               {err}
// //               <br />
// //               Start MySQL, load the starter dataset, then run FastAPI.
// //             </div>
// //           </div>
// //         )}

// //         {/* OVERVIEW DASHBOARD */}
// //         {tab === 'Overview' ? (
// //           <>
// //             {/* METRIC CARDS */}
// //             <section className="metrics">
// //               {metrics.map(([name, value, Icon]) => (
// //                 <div className="metric" key={name}>
// //                   <div className="metrichead">
// //                     <span>{name}</span>
// //                     <Icon size={18} />
// //                   </div>

// //                   <strong>
// //                     {value ?? 0}
// //                   </strong>

// //                   <small>
// //                     Live database metric
// //                   </small>
// //                 </div>
// //               ))}
// //             </section>

// //             {/* CHARTS */}
// //             <section className="charts">

// //               {/* MESSAGING FUNNEL */}
// //               <div className="panel">
// //                 <div className="paneltitle">
// //                   <div>
// //                     <b>Messaging funnel</b>
// //                     <small>
// //                       Communication event progression
// //                     </small>
// //                   </div>

// //                   <span className="pill">
// //                     ALL CHANNELS
// //                   </span>
// //                 </div>

// //                 <ResponsiveContainer width="100%" height={260}>
// //                   <BarChart data={chart}>
// //                     <XAxis dataKey="name" />
// //                     <YAxis />
// //                     <Tooltip />

// //                     <Bar
// //                       dataKey="value"
// //                       fill="#5367e8"
// //                       radius={[6, 6, 0, 0]}
// //                     />
// //                   </BarChart>
// //                 </ResponsiveContainer>
// //               </div>

// //               {/* CART LIFECYCLE */}
// //               <div className="panel">
// //                 <div className="paneltitle">
// //                   <div>
// //                     <b>Cart lifecycle</b>
// //                     <small>
// //                       Current cart distribution
// //                     </small>
// //                   </div>
// //                 </div>

// //                 <ResponsiveContainer width="100%" height={260}>
// //                   <PieChart>
// //                     <Pie
// //                       data={[
// //                         {
// //                           name: 'Abandoned',
// //                           value: data.abandoned_carts || 0
// //                         },
// //                         {
// //                           name: 'Active',
// //                           value: data.active_carts || 0
// //                         },
// //                         {
// //                           name: 'Recovered',
// //                           value: data.recovered_carts || 0
// //                         }
// //                       ]}
// //                       dataKey="value"
// //                       nameKey="name"
// //                       innerRadius={62}
// //                       outerRadius={92}
// //                       paddingAngle={4}
// //                     >
// //                       {[0, 1, 2].map(index => (
// //                         <Cell
// //                           key={index}
// //                           fill={['#5367e8', '#19a88b', '#f2a64b'][index]}
// //                         />
// //                       ))}
// //                     </Pie>

// //                     <Tooltip />
// //                   </PieChart>
// //                 </ResponsiveContainer>
// //               </div>
// //             </section>

// //             {/* BUSINESS RULES */}
// //             <section className="panel insight">
// //               <div>
// //                 <b>
// //                   <ShieldCheck size={18} />
// //                   Consent and suppression guardrails
// //                 </b>

// //                 <p>
// //                   Messages are eligible only when the latest effective
// //                   channel consent is OPTED_IN. Unknown and withdrawn
// //                   consent is suppressed.
// //                 </p>
// //               </div>

// //               <div>
// //                 <b>
// //                   <ChartNoAxesCombined size={18} />
// //                   Attribution policy
// //                 </b>

// //                 <p>
// //                   Single-touch, 7-day attribution. A qualifying click
// //                   outranks open and delivery; one order receives at
// //                   most one campaign credit.
// //                 </p>
// //               </div>
// //             </section>
// //           </>
// //         ) : tab === 'Consent Management' ? (
// //           /* CONSENT MANAGEMENT */
// //           <div>
// //             <section className="metrics">
// //               <div className="metric">
// //                 <div className="metrichead">
// //                   <span>Total consent records</span>
// //                   <ShieldCheck size={18} />
// //                 </div>
// //                 <strong>{rows.length}</strong>
// //                 <small>Records from the database</small>
// //               </div>

// //               <div className="metric">
// //                 <div className="metrichead">
// //                   <span>Opted in</span>
// //                   <ShieldCheck size={18} />
// //                 </div>
// //                 <strong>{consentOptedIn}</strong>
// //                 <small>Permission granted</small>
// //               </div>

// //               <div className="metric">
// //                 <div className="metrichead">
// //                   <span>Opted out</span>
// //                   <AlertTriangle size={18} />
// //                 </div>
// //                 <strong>{consentOptedOut}</strong>
// //                 <small>Permission withdrawn</small>
// //               </div>
// //             </section>

// //             <section className="panel" style={{ marginBottom: 20 }}>
// //               <div className="paneltitle">
// //                 <div>
// //                   <b>Search and filter consents</b>
// //                   <small>Search by customer and filter by channel or status</small>
// //                 </div>
// //               </div>

// //               <div style={{
// //                 display: 'flex',
// //                 flexWrap: 'wrap',
// //                 gap: 12,
// //                 padding: 16
// //               }}>
// //                 <input
// //                   type="text"
// //                   value={consentSearch}
// //                   onChange={event => setConsentSearch(event.target.value)}
// //                   placeholder="Search customer name or ID"
// //                   style={{
// //                     flex: '2 1 220px',
// //                     minWidth: 200,
// //                     padding: 11,
// //                     border: '1px solid #dce1ed',
// //                     borderRadius: 8,
// //                     font: 'inherit'
// //                   }}
// //                 />

// //                 <select
// //                   value={consentChannel}
// //                   onChange={event => setConsentChannel(event.target.value)}
// //                   style={{
// //                     flex: '1 1 150px',
// //                     padding: 11,
// //                     border: '1px solid #dce1ed',
// //                     borderRadius: 8,
// //                     background: '#fff',
// //                     font: 'inherit'
// //                   }}
// //                 >
// //                   <option value="ALL">All channels</option>
// //                   <option value="EMAIL">Email</option>
// //                   <option value="SMS">SMS</option>
// //                 </select>

// //                 <select
// //                   value={consentStatus}
// //                   onChange={event => setConsentStatus(event.target.value)}
// //                   style={{
// //                     flex: '1 1 150px',
// //                     padding: 11,
// //                     border: '1px solid #dce1ed',
// //                     borderRadius: 8,
// //                     background: '#fff',
// //                     font: 'inherit'
// //                   }}
// //                 >
// //                   <option value="ALL">All statuses</option>
// //                   <option value="OPTED_IN">Opted in</option>
// //                   <option value="OPTED_OUT">Opted out</option>
// //                 </select>
// //               </div>
// //             </section>

// //             <section className="panel tablepanel">
// //               <div className="paneltitle">
// //                 <div>
// //                   <b>Customer consent records</b>
// //                   <small>Consent history stored in MySQL</small>
// //                 </div>
// //                 <span className="pill">
// //                   {filteredConsentRows.length} RECORDS
// //                 </span>
// //               </div>

// //               {loading ? (
// //                 <div className="empty">Loading consent records...</div>
// //               ) : (
// //                 <div className="tablewrap">
// //                   <table>
// //                     <thead>
// //                       <tr>
// //                         <th>Consent ID</th>
// //                         <th>Customer ID</th>
// //                         <th>Customer Name</th>
// //                         <th>Channel</th>
// //                         <th>Status</th>
// //                         <th>Effective At</th>
// //                         <th>Withdrawn At</th>
// //                         <th>Source</th>
// //                       </tr>
// //                     </thead>
// //                     <tbody>
// //                       {filteredConsentRows.map((row, index) => (
// //                         <tr key={row.consent_id || index}>
// //                           <td>{displayValue(row.consent_id)}</td>
// //                           <td>{displayValue(row.customer_id)}</td>
// //                           <td>{displayValue(row.customer_name)}</td>
// //                           <td>{displayValue(row.channel)}</td>
// //                           <td>{displayValue(row.status)}</td>
// //                           <td>{displayValue(row.effective_at)}</td>
// //                           <td>{displayValue(row.withdrawn_at)}</td>
// //                           <td>{displayValue(row.source)}</td>
// //                         </tr>
// //                       ))}
// //                     </tbody>
// //                   </table>

// //                   {filteredConsentRows.length === 0 && (
// //                     <div className="empty">
// //                       No consent records match the selected filters.
// //                     </div>
// //                   )}
// //                 </div>
// //               )}
// //             </section>
// //           </div>
// //         ) : (
// //           /* DATA TABLES */
// //           <section className="panel tablepanel">
// //             <div className="paneltitle">
// //               <div>
// //                 <b>{tab}</b>
// //                 <small>
// //                   Records from the MySQL database
// //                 </small>
// //               </div>

// //               <span className="pill">
// //                 {rows.length} RECORDS
// //               </span>
// //             </div>

// //             {loading ? (
// //               <div className="empty">
// //                 Loading records...
// //               </div>
// //             ) : rows.length === 0 ? (
// //               <div className="empty">
// //                 No records available. Check the database connection and load the dataset.
// //               </div>
// //             ) : (
// //               <div className="tablewrap">

// //                 {/* SPECIAL ORDERS TABLE */}
// //                 {tab === 'Orders' ? (
// //                   <table>
// //                     <thead>
// //                       <tr>
// //                         <th>Order ID</th>
// //                         <th>Customer ID</th>
// //                         <th>Order Total</th>
// //                         <th>Ordered At</th>
// //                         <th>Attribution Status</th>
// //                         <th>Attribution ID</th>
// //                         <th>Campaign ID</th>
// //                         <th>Send ID</th>
// //                         <th>Attributed Revenue</th>
// //                       </tr>
// //                     </thead>

// //                     <tbody>
// //                       {rows.map((row, index) => {
// //                         const attributed = row.attribution_id != null;

// //                         return (
// //                           <tr key={index}>
// //                             <td>{displayValue(row.order_id)}</td>
// //                             <td>{displayValue(row.customer_id)}</td>
// //                             <td>
// //                               ₹{Number(row.order_total || 0).toLocaleString('en-IN')}
// //                             </td>
// //                             <td>{displayValue(row.ordered_at)}</td>
// //                             <td>
// //                               {attributed ? 'Attributed' : 'Not Attributed'}
// //                             </td>
// //                             <td>
// //                               {row.attribution_id ?? 'Not Attributed'}
// //                             </td>
// //                             <td>
// //                               {row.attributed_campaign_id ?? 'Not Attributed'}
// //                             </td>
// //                             <td>
// //                               {row.attributed_send_id ?? 'Not Attributed'}
// //                             </td>
// //                             <td>
// //                               {attributed
// //                                 ? `₹${Number(row.attributed_revenue || 0).toLocaleString('en-IN')}`
// //                                 : '—'}
// //                             </td>
// //                           </tr>
// //                         );
// //                       })}
// //                     </tbody>
// //                   </table>

// //                 ) : tab === 'Audit Decisions' ? (
// //                   /* SPECIAL AUDIT DECISIONS TABLE */
// //                   <table>
// //                     <thead>
// //                       <tr>
// //                         <th>Decision ID</th>
// //                         <th>Customer ID</th>
// //                         <th>Cart ID</th>
// //                         <th>Channel</th>
// //                         <th>Decision</th>
// //                         <th>Reason Code</th>
// //                         <th>Explanation</th>
// //                         <th>Decided At</th>
// //                       </tr>
// //                     </thead>

// //                     <tbody>
// //                       {rows.map((row, index) => (
// //                         <tr key={index}>
// //                           <td>{displayValue(row.decision_id)}</td>
// //                           <td>{displayValue(row.customer_id)}</td>
// //                           <td>{displayValue(row.cart_id)}</td>
// //                           <td>{displayValue(row.channel)}</td>
// //                           <td>{displayValue(row.decision)}</td>
// //                           <td>{displayValue(row.reason_code)}</td>
// //                           <td>{displayValue(row.detail)}</td>
// //                           <td>{displayValue(row.decided_at)}</td>
// //                         </tr>
// //                       ))}
// //                     </tbody>
// //                   </table>

// //                 ) : (
// //                   /* DEFAULT TABLE FOR OTHER TABS */
// //                   <table>
// //                     <thead>
// //                       <tr>
// //                         {Object.keys(rows[0]).slice(0, 8).map(key => (
// //                           <th key={key}>
// //                             {formatColumn(key)}
// //                           </th>
// //                         ))}
// //                       </tr>
// //                     </thead>

// //                     <tbody>
// //                       {rows.map((row, index) => (
// //                         <tr key={index}>
// //                           {Object.keys(row).slice(0, 8).map(key => (
// //                             <td key={key}>
// //                               {displayValue(row[key])}
// //                             </td>
// //                           ))}
// //                         </tr>
// //                       ))}
// //                     </tbody>
// //                   </table>
// //                 )}
// //               </div>
// //             )}
// //           </section>
// //         )}

// //         {/* FOOTER */}
// //         <footer>
// //           <span>
// //             CartRecover · Abandoned Cart Recovery Platform
// //           </span>

// //           <span>
// //             DEMO DATA · NO LIVE MESSAGES SENT
// //           </span>
// //         </footer>
// //       </main>
// //     </div>
// //   );
// // }


// import { useEffect, useState } from 'react';

// import {
//   ResponsiveContainer,
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   Tooltip,
//   PieChart,
//   Pie,
//   Cell
// } from 'recharts';

// import {
//   ShoppingCart,
//   Users,
//   Mail,
//   IndianRupee,
//   ShieldCheck,
//   AlertTriangle,
//   RefreshCw,
//   LayoutDashboard,
//   Package,
//   Send,
//   ChartNoAxesCombined
// } from 'lucide-react';

// const API = 'http://127.0.0.1:8000/api';

// export default function App() {
//   const [data, setData] = useState({});
//   const [tab, setTab] = useState('Overview');
//   const [rows, setRows] = useState([]);
//   const [err, setErr] = useState('');
//   const [loading, setLoading] = useState(false);
//   // Consent management filters
// const [consentSearch, setConsentSearch] = useState('');
// const [consentChannel, setConsentChannel] = useState('ALL');
// const [consentStatus, setConsentStatus] = useState('ALL');

//   // Campaign creation form state
//   const [campaignForm, setCampaignForm] = useState({
//     campaign_name: '',
//     channel: 'EMAIL',
//     variant: 'A',
//     target_audience: 'ABANDONED_CARTS',
//     scheduled_at: ''
//   });
//   const [campaignSubmitting, setCampaignSubmitting] = useState(false);
//   const [campaignMessage, setCampaignMessage] = useState('');
//   const [campaignError, setCampaignError] = useState('');
//   // Campaign editing state
// const [editingCampaign, setEditingCampaign] = useState(null);
// const [editSubmitting, setEditSubmitting] = useState(false);
// const [editMessage, setEditMessage] = useState('');
// const [editError, setEditError] = useState('');

//   // Load dashboard data
//   const load = async () => {
//     try {
//       setErr('');

//       const response = await fetch(API + '/dashboard');

//       if (!response.ok) {
//         throw new Error(await response.text());
//       }

//       setData(await response.json());
//     } catch (error) {
//       setErr(error.message || 'API unavailable');
//     }
//   };

//   // Load records for the selected tab
//   const loadRows = async (selectedTab) => {
//     const endpoints = {
//       Customers: '/customers',
//       Carts: '/carts',
//       Campaigns: '/campaigns',
//       'Send History': '/sends',
//       Orders: '/orders?limit=500',
//       Anomalies: '/anomalies',
//       'Audit Decisions': '/audit-decisions?limit=500',
//       'Consent Management': '/consents?limit=1000'
//     };

//     if (!endpoints[selectedTab]) {
//       setRows([]);
//       return;
//     }

//     try {
//       setLoading(true);

//       const response = await fetch(API + endpoints[selectedTab]);

//       if (!response.ok) {
//         throw new Error('Unable to fetch records');
//       }

//       const result = await response.json();
//       setRows(Array.isArray(result) ? result : []);
//     } catch {
//       setRows([]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Initial dashboard loading
//   useEffect(() => {
//     load();
//   }, []);

//   // Load records whenever the selected tab changes
//   useEffect(() => {
//     loadRows(tab);
//   }, [tab]);

//   // Navigation items
//   const nav = [
//     ['Overview', LayoutDashboard],
//     ['Customers', Users],
//     ['Carts', ShoppingCart],
//     ['Campaigns', Send],
//     ['Send History', Mail],
//     ['Orders', Package],
//     ['Anomalies', AlertTriangle],
//     // ['Audit Decisions', ShieldCheck]
//     ['Audit Decisions', ShieldCheck],
//     ['Consent Management', ShieldCheck]
//   ];

//   // Dashboard metrics
//   const metrics = [
//     ['Customers', data.customers, Users],
//     ['Total carts', data.carts, ShoppingCart],
//     ['Abandoned', data.abandoned_carts, AlertTriangle],
//     ['Recovered', data.recovered_carts, RefreshCw],
//     ['Messages delivered', data.messages_delivered, Mail],
//     ['Orders', data.orders, Package],
//     ['Attributed orders', data.attributed_orders, ChartNoAxesCombined],
//     [
//       'Recovered revenue',
//       `₹${(data.recovered_revenue || 0).toLocaleString('en-IN')}`,
//       IndianRupee
//     ]
//   ];

//   // Messaging funnel data
//   const chart = [
//     {
//       name: 'Attempted',
//       value: data.messages_attempted || 0
//     },
//     {
//       name: 'Delivered',
//       value: data.messages_delivered || 0
//     },
//     {
//       name: 'Opened',
//       value: data.messages_opened || 0
//     },
//     {
//       name: 'Clicked',
//       value: data.messages_clicked || 0
//     }
//   ];

//   // Refresh dashboard and current table
//   const refreshData = () => {
//     load();

//     if (tab !== 'Overview') {
//       loadRows(tab);
//     }
//   };

//   // Display values safely
//   const displayValue = (value) => {
//     return value == null ? '—' : String(value);
//   };

//   // Format table column names
//   const formatColumn = (key) => {
//     return key.replace(/_/g, ' ');
//   };
//   // Consent management summary and filtering
// const consentOptedIn = rows.filter(
//   row => row.status === 'OPTED_IN'
// ).length;

// const consentOptedOut = rows.filter(
//   row => row.status === 'OPTED_OUT'
// ).length;

// const filteredConsentRows = rows.filter(row => {
//   const search = consentSearch.toLowerCase();

//   const matchesSearch =
//     String(row.customer_name || '').toLowerCase().includes(search) ||
//     String(row.customer_id || '').toLowerCase().includes(search);

//   const matchesChannel =
//     consentChannel === 'ALL' || row.channel === consentChannel;

//   const matchesStatus =
//     consentStatus === 'ALL' || row.status === consentStatus;

//   return matchesSearch && matchesChannel && matchesStatus;
// });

//   // Create a draft campaign through the FastAPI endpoint.
//   const createCampaign = async (event) => {
//     event.preventDefault();
//     setCampaignSubmitting(true);
//     setCampaignMessage('');
//     setCampaignError('');

//     try {
//       const payload = {
//         ...campaignForm,
//         // datetime-local already provides local YYYY-MM-DDTHH:mm format.
//         // Append seconds while keeping the selected local time unchanged.
//         scheduled_at: campaignForm.scheduled_at.length === 16
//           ? `${campaignForm.scheduled_at}:00`
//           : campaignForm.scheduled_at
//       };

//       const response = await fetch(API + '/campaigns', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(payload)
//       });

//       const result = await response.json();
//       if (!response.ok) {
//         throw new Error(result.detail || 'Campaign creation failed.');
//       }

//       setCampaignMessage(
//         `Campaign created successfully. ID: ${result.campaign_id} (DRAFT)`
//       );
//       setCampaignForm({
//         campaign_name: '',
//         channel: 'EMAIL',
//         variant: 'A',
//         target_audience: 'ABANDONED_CARTS',
//         scheduled_at: ''
//       });
//       await loadRows('Campaigns');
//       await load();
//     } catch (error) {
//       setCampaignError(error.message || 'Unable to create campaign.');
//     } finally {
//       setCampaignSubmitting(false);
//     }
//   };
//     // Open a campaign for editing
//   const startEditCampaign = (campaign) => {
//     setEditingCampaign({
//       ...campaign,
//       scheduled_at: campaign.scheduled_at
//         ? String(campaign.scheduled_at).slice(0, 16)
//         : ''
//     });

//     setEditMessage('');
//     setEditError('');
//   };

//   // Save campaign changes through the PATCH API
//   const updateCampaign = async (event) => {
//     event.preventDefault();

//     if (!editingCampaign) return;

//     setEditSubmitting(true);
//     setEditMessage('');
//     setEditError('');

//     try {
//       const payload = {
//         campaign_name: editingCampaign.campaign_name,
//         channel: editingCampaign.channel,
//         variant: editingCampaign.variant,
//         target_audience: editingCampaign.target_audience,
//         scheduled_at: editingCampaign.scheduled_at.length === 16
//           ? `${editingCampaign.scheduled_at}:00`
//           : editingCampaign.scheduled_at
//       };

//       const response = await fetch(
//         `${API}/campaigns/${encodeURIComponent(editingCampaign.campaign_id)}`,
//         {
//           method: 'PATCH',
//           headers: {
//             'Content-Type': 'application/json'
//           },
//           body: JSON.stringify(payload)
//         }
//       );

//       const result = await response.json();

//       if (!response.ok) {
//         throw new Error(result.detail || 'Campaign update failed.');
//       }

//       setEditMessage(
//         `Campaign ${result.campaign_id} updated successfully.`
//       );

//       setEditingCampaign(null);

//       await loadRows('Campaigns');
//       await load();

//     } catch (error) {
//       setEditError(error.message || 'Unable to update campaign.');
//     } finally {
//       setEditSubmitting(false);
//     }
//   };

//   return (
//     <div className="shell">

//       {/* SIDEBAR */}
//       <aside>
//         <div className="brand">
//           <div className="brandicon">
//             CR
//           </div>

//           <div>
//             <b>CartRecover</b>
//             <small>COMMERCE INTELLIGENCE</small>
//           </div>
//         </div>

//         <div className="navlabel">
//           WORKSPACE
//         </div>

//         {nav.map(([name, Icon]) => (
//           <button
//             className={tab === name ? 'active' : ''}
//             onClick={() => setTab(name)}
//             key={name}
//           >
//             <Icon size={18} />
//             {name}
//           </button>
//         ))}

//         <div className="sidebottom">
//           <ShieldCheck size={18} />

//           Consent-first orchestration

//           <small>
//             MySQL · Local environment
//           </small>
//         </div>
//       </aside>

//       {/* MAIN CONTENT */}
//       <main>

//         {/* HEADER */}
//         <header>
//           <div>
//             <span className="eyebrow">
//               OPERATIONS / {tab.toUpperCase()}
//             </span>

//             <h1>
//               {tab === 'Overview' ? 'Recovery overview' : tab}
//             </h1>

//             <p>
//               Monitor recovery performance, customer permissions and conversion outcomes.
//             </p>
//           </div>

//           <button
//             className="refresh"
//             onClick={refreshData}
//           >
//             <RefreshCw size={16} />
//             Refresh data
//           </button>
//         </header>

//         {/* ERROR MESSAGE */}
//         {err && (
//           <div className="error">
//             <AlertTriangle size={18} />

//             <div>
//               <b>Backend connection unavailable</b>
//               <br />
//               {err}
//               <br />
//               Start MySQL, load the starter dataset, then run FastAPI.
//             </div>
//           </div>
//         )}

//         {/* OVERVIEW DASHBOARD */}
//         {tab === 'Overview' ? (
//           <>
//             {/* METRIC CARDS */}
//             <section className="metrics">
//               {metrics.map(([name, value, Icon]) => (
//                 <div className="metric" key={name}>
//                   <div className="metrichead">
//                     <span>{name}</span>
//                     <Icon size={18} />
//                   </div>

//                   <strong>
//                     {value ?? 0}
//                   </strong>

//                   <small>
//                     Live database metric
//                   </small>
//                 </div>
//               ))}
//             </section>

//             {/* CHARTS */}
//             <section className="charts">

//               {/* MESSAGING FUNNEL */}
//               <div className="panel">
//                 <div className="paneltitle">
//                   <div>
//                     <b>Messaging funnel</b>
//                     <small>
//                       Communication event progression
//                     </small>
//                   </div>

//                   <span className="pill">
//                     ALL CHANNELS
//                   </span>
//                 </div>

//                 <ResponsiveContainer width="100%" height={260}>
//                   <BarChart data={chart}>
//                     <XAxis dataKey="name" />
//                     <YAxis />
//                     <Tooltip />

//                     <Bar
//                       dataKey="value"
//                       fill="#5367e8"
//                       radius={[6, 6, 0, 0]}
//                     />
//                   </BarChart>
//                 </ResponsiveContainer>
//               </div>

//               {/* CART LIFECYCLE */}
//               <div className="panel">
//                 <div className="paneltitle">
//                   <div>
//                     <b>Cart lifecycle</b>
//                     <small>
//                       Current cart distribution
//                     </small>
//                   </div>
//                 </div>

//                 <ResponsiveContainer width="100%" height={260}>
//                   <PieChart>
//                     <Pie
//                       data={[
//                         {
//                           name: 'Abandoned',
//                           value: data.abandoned_carts || 0
//                         },
//                         {
//                           name: 'Active',
//                           value: data.active_carts || 0
//                         },
//                         {
//                           name: 'Recovered',
//                           value: data.recovered_carts || 0
//                         }
//                       ]}
//                       dataKey="value"
//                       nameKey="name"
//                       innerRadius={62}
//                       outerRadius={92}
//                       paddingAngle={4}
//                     >
//                       {[0, 1, 2].map(index => (
//                         <Cell
//                           key={index}
//                           fill={['#5367e8', '#19a88b', '#f2a64b'][index]}
//                         />
//                       ))}
//                     </Pie>

//                     <Tooltip />
//                   </PieChart>
//                 </ResponsiveContainer>
//               </div>
//             </section>

//             {/* BUSINESS RULES */}
//             <section className="panel insight">
//               <div>
//                 <b>
//                   <ShieldCheck size={18} />
//                   Consent and suppression guardrails
//                 </b>

//                 <p>
//                   Messages are eligible only when the latest effective
//                   channel consent is OPTED_IN. Unknown and withdrawn
//                   consent is suppressed.
//                 </p>
//               </div>

//               <div>
//                 <b>
//                   <ChartNoAxesCombined size={18} />
//                   Attribution policy
//                 </b>

//                 <p>
//                   Single-touch, 7-day attribution. A qualifying click
//                   outranks open and delivery; one order receives at
//                   most one campaign credit.
//                 </p>
//               </div>
//             </section>
//           </>
//         ) : tab === 'Campaigns' ? (
//           /* CAMPAIGN MANAGEMENT AND CREATE CAMPAIGN */
//           <div>
//             <section className="panel" style={{ marginBottom: 20 }}>
//               <div className="paneltitle">
//                 <div>
//                   <b>Create a recovery campaign</b>
//                   <small>Create a draft campaign. No messages are sent from this form.</small>
//                 </div>
//               </div>

//               <form
//                 onSubmit={createCampaign}
//                 style={{
//                   display: 'grid',
//                   gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
//                   gap: 14,
//                   padding: 16
//                 }}
//               >
//                 <label style={{ display: 'grid', gap: 7 }}>
//                   <span>Campaign name</span>
//                   <input
//                     type="text"
//                     required
//                     maxLength={120}
//                     value={campaignForm.campaign_name}
//                     onChange={event => setCampaignForm({ ...campaignForm, campaign_name: event.target.value })}
//                     placeholder="e.g. Weekend Cart Recovery"
//                     style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
//                   />
//                 </label>

//                 <label style={{ display: 'grid', gap: 7 }}>
//                   <span>Channel</span>
//                   <select
//                     value={campaignForm.channel}
//                     onChange={event => setCampaignForm({ ...campaignForm, channel: event.target.value })}
//                     style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', font: 'inherit' }}
//                   >
//                     <option value="EMAIL">Email</option>
//                     <option value="SMS">SMS</option>
//                   </select>
//                 </label>

//                 <label style={{ display: 'grid', gap: 7 }}>
//                   <span>Variant</span>
//                   <select
//                     value={campaignForm.variant}
//                     onChange={event => setCampaignForm({ ...campaignForm, variant: event.target.value })}
//                     style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', font: 'inherit' }}
//                   >
//                     <option value="A">A</option>
//                     <option value="B">B</option>
//                     <option value="C">C</option>
//                   </select>
//                 </label>

//                 <label style={{ display: 'grid', gap: 7 }}>
//                   <span>Target audience</span>
//                   <input
//                     type="text"
//                     required
//                     maxLength={120}
//                     value={campaignForm.target_audience}
//                     onChange={event => setCampaignForm({ ...campaignForm, target_audience: event.target.value })}
//                     style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
//                   />
//                 </label>

//                 <label style={{ display: 'grid', gap: 7 }}>
//                   <span>Scheduled at</span>
//                   <input
//                     type="datetime-local"
//                     required
//                     value={campaignForm.scheduled_at}
//                     onChange={event => setCampaignForm({ ...campaignForm, scheduled_at: event.target.value })}
//                     style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
//                   />
//                 </label>

//                 <div style={{ display: 'flex', alignItems: 'end' }}>
//                   <button
//                     type="submit"
//                     disabled={campaignSubmitting}
//                     style={{ padding: '11px 18px', border: 0, borderRadius: 8, background: '#5367e8', color: '#fff', font: 'inherit', cursor: campaignSubmitting ? 'wait' : 'pointer', opacity: campaignSubmitting ? 0.7 : 1 }}
//                   >
//                     {campaignSubmitting ? 'Creating...' : 'Create draft campaign'}
//                   </button>
//                 </div>
//               </form>

//               {campaignMessage && (
//                 <div style={{ margin: '0 16px 16px', padding: 12, borderRadius: 8, background: '#e8f7ef', color: '#176b3a' }}>
//                   {campaignMessage}
//                 </div>
//               )}
//               {campaignError && (
//                 <div style={{ margin: '0 16px 16px', padding: 12, borderRadius: 8, background: '#fff0f0', color: '#a12626' }}>
//                   {campaignError}
//                 </div>
//               )}
//             </section>

//             <section className="panel tablepanel">
//               <div className="paneltitle">
//                 <div>
//                   <b>Campaigns</b>
//                   <small>Campaign records from the MySQL database</small>
//                 </div>
//                 <span className="pill">{rows.length} RECORDS</span>
//               </div>

//               {loading ? (
//                 <div className="empty">Loading campaigns...</div>
//               ) : rows.length === 0 ? (
//                 <div className="empty">No campaigns found. Create your first draft campaign above.</div>
//               ) : (
//                 <div className="tablewrap">
//                   <table>
//                     <thead>
//                       <tr>
//                         <th>Campaign ID</th>
//                         <th>Campaign Name</th>
//                         <th>Channel</th>
//                         <th>Variant</th>
//                         <th>Target Audience</th>
//                         <th>Scheduled At</th>
//                         <th>Status</th>
//                         <th>Created At</th>
//                         <th>Actions</th>
//                       </tr>
//                     </thead>
//                     <tbody>
//                       {rows.map((row, index) => (
//                         <tr key={row.campaign_id || index}>
//                           <td>{displayValue(row.campaign_id)}</td>
//                           <td>{displayValue(row.campaign_name)}</td>
//                           <td>{displayValue(row.channel)}</td>
//                           <td>{displayValue(row.variant)}</td>
//                           <td>{displayValue(row.target_audience)}</td>
//                           <td>{displayValue(row.scheduled_at)}</td>
//                           <td>{displayValue(row.status)}</td>
//                           <td>{displayValue(row.created_at)}</td>
//                           <td>
//                             {row.status === 'DRAFT' ? (
//                               <button
//                               type="button"
//                               onClick={() => startEditCampaign(row)}
//                               style={{
//                                 padding: '7px 12px',
//                                 border: '1px solid #5367e8',
//                                 borderRadius: 6,
//                                 background: '#fff',
//                                 color: '#5367e8',
//                                 cursor: 'pointer'
//                               }}
//                               >
//               Edit
//             </button>
//           ) : (
//             'Not editable'
//           )}
//         </td>
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>
//                 </div>
//               )}
//             </section>
//           </div>
//         ) : tab === 'Consent Management' ? (
//           /* CONSENT MANAGEMENT */
//           <div>
//             <section className="metrics">
//               <div className="metric">
//                 <div className="metrichead">
//                   <span>Total consent records</span>
//                   <ShieldCheck size={18} />
//                 </div>
//                 <strong>{rows.length}</strong>
//                 <small>Records from the database</small>
//               </div>

//               <div className="metric">
//                 <div className="metrichead">
//                   <span>Opted in</span>
//                   <ShieldCheck size={18} />
//                 </div>
//                 <strong>{consentOptedIn}</strong>
//                 <small>Permission granted</small>
//               </div>

//               <div className="metric">
//                 <div className="metrichead">
//                   <span>Opted out</span>
//                   <AlertTriangle size={18} />
//                 </div>
//                 <strong>{consentOptedOut}</strong>
//                 <small>Permission withdrawn</small>
//               </div>
//             </section>

//             <section className="panel" style={{ marginBottom: 20 }}>
//               <div className="paneltitle">
//                 <div>
//                   <b>Search and filter consents</b>
//                   <small>Search by customer and filter by channel or status</small>
//                 </div>
//               </div>

//               <div style={{
//                 display: 'flex',
//                 flexWrap: 'wrap',
//                 gap: 12,
//                 padding: 16
//               }}>
//                 <input
//                   type="text"
//                   value={consentSearch}
//                   onChange={event => setConsentSearch(event.target.value)}
//                   placeholder="Search customer name or ID"
//                   style={{
//                     flex: '2 1 220px',
//                     minWidth: 200,
//                     padding: 11,
//                     border: '1px solid #dce1ed',
//                     borderRadius: 8,
//                     font: 'inherit'
//                   }}
//                 />

//                 <select
//                   value={consentChannel}
//                   onChange={event => setConsentChannel(event.target.value)}
//                   style={{
//                     flex: '1 1 150px',
//                     padding: 11,
//                     border: '1px solid #dce1ed',
//                     borderRadius: 8,
//                     background: '#fff',
//                     font: 'inherit'
//                   }}
//                 >
//                   <option value="ALL">All channels</option>
//                   <option value="EMAIL">Email</option>
//                   <option value="SMS">SMS</option>
//                 </select>

//                 <select
//                   value={consentStatus}
//                   onChange={event => setConsentStatus(event.target.value)}
//                   style={{
//                     flex: '1 1 150px',
//                     padding: 11,
//                     border: '1px solid #dce1ed',
//                     borderRadius: 8,
//                     background: '#fff',
//                     font: 'inherit'
//                   }}
//                 >
//                   <option value="ALL">All statuses</option>
//                   <option value="OPTED_IN">Opted in</option>
//                   <option value="OPTED_OUT">Opted out</option>
//                 </select>
//               </div>
//             </section>

//             <section className="panel tablepanel">
//               <div className="paneltitle">
//                 <div>
//                   <b>Customer consent records</b>
//                   <small>Consent history stored in MySQL</small>
//                 </div>
//                 <span className="pill">
//                   {filteredConsentRows.length} RECORDS
//                 </span>
//               </div>

//               {loading ? (
//                 <div className="empty">Loading consent records...</div>
//               ) : (
//                 <div className="tablewrap">
//                   <table>
//                     <thead>
//                       <tr>
//                         <th>Consent ID</th>
//                         <th>Customer ID</th>
//                         <th>Customer Name</th>
//                         <th>Channel</th>
//                         <th>Status</th>
//                         <th>Effective At</th>
//                         <th>Withdrawn At</th>
//                         <th>Source</th>
//                       </tr>
//                     </thead>
//                     <tbody>
//                       {filteredConsentRows.map((row, index) => (
//                         <tr key={row.consent_id || index}>
//                           <td>{displayValue(row.consent_id)}</td>
//                           <td>{displayValue(row.customer_id)}</td>
//                           <td>{displayValue(row.customer_name)}</td>
//                           <td>{displayValue(row.channel)}</td>
//                           <td>{displayValue(row.status)}</td>
//                           <td>{displayValue(row.effective_at)}</td>
//                           <td>{displayValue(row.withdrawn_at)}</td>
//                           <td>{displayValue(row.source)}</td>
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>

//                   {filteredConsentRows.length === 0 && (
//                     <div className="empty">
//                       No consent records match the selected filters.
//                     </div>
//                   )}
//                 </div>
//               )}
//             </section>
//           </div>
//         ) : (
//           /* DATA TABLES */
//           <section className="panel tablepanel">
//             <div className="paneltitle">
//               <div>
//                 <b>{tab}</b>
//                 <small>
//                   Records from the MySQL database
//                 </small>
//               </div>

//               <span className="pill">
//                 {rows.length} RECORDS
//               </span>
//             </div>

//             {loading ? (
//               <div className="empty">
//                 Loading records...
//               </div>
//             ) : rows.length === 0 ? (
//               <div className="empty">
//                 No records available. Check the database connection and load the dataset.
//               </div>
//             ) : (
//               <div className="tablewrap">

//                 {/* SPECIAL ORDERS TABLE */}
//                 {tab === 'Orders' ? (
//                   <table>
//                     <thead>
//                       <tr>
//                         <th>Order ID</th>
//                         <th>Customer ID</th>
//                         <th>Order Total</th>
//                         <th>Ordered At</th>
//                         <th>Attribution Status</th>
//                         <th>Attribution ID</th>
//                         <th>Campaign ID</th>
//                         <th>Send ID</th>
//                         <th>Attributed Revenue</th>
//                       </tr>
//                     </thead>

//                     <tbody>
//                       {rows.map((row, index) => {
//                         const attributed = row.attribution_id != null;

//                         return (
//                           <tr key={index}>
//                             <td>{displayValue(row.order_id)}</td>
//                             <td>{displayValue(row.customer_id)}</td>
//                             <td>
//                               ₹{Number(row.order_total || 0).toLocaleString('en-IN')}
//                             </td>
//                             <td>{displayValue(row.ordered_at)}</td>
//                             <td>
//                               {attributed ? 'Attributed' : 'Not Attributed'}
//                             </td>
//                             <td>
//                               {row.attribution_id ?? 'Not Attributed'}
//                             </td>
//                             <td>
//                               {row.attributed_campaign_id ?? 'Not Attributed'}
//                             </td>
//                             <td>
//                               {row.attributed_send_id ?? 'Not Attributed'}
//                             </td>
//                             <td>
//                               {attributed
//                                 ? `₹${Number(row.attributed_revenue || 0).toLocaleString('en-IN')}`
//                                 : '—'}
//                             </td>
//                           </tr>
//                         );
//                       })}
//                     </tbody>
//                   </table>

//                 ) : tab === 'Audit Decisions' ? (
//                   /* SPECIAL AUDIT DECISIONS TABLE */
//                   <table>
//                     <thead>
//                       <tr>
//                         <th>Decision ID</th>
//                         <th>Customer ID</th>
//                         <th>Cart ID</th>
//                         <th>Channel</th>
//                         <th>Decision</th>
//                         <th>Reason Code</th>
//                         <th>Explanation</th>
//                         <th>Decided At</th>
//                       </tr>
//                     </thead>

//                     <tbody>
//                       {rows.map((row, index) => (
//                         <tr key={index}>
//                           <td>{displayValue(row.decision_id)}</td>
//                           <td>{displayValue(row.customer_id)}</td>
//                           <td>{displayValue(row.cart_id)}</td>
//                           <td>{displayValue(row.channel)}</td>
//                           <td>{displayValue(row.decision)}</td>
//                           <td>{displayValue(row.reason_code)}</td>
//                           <td>{displayValue(row.detail)}</td>
//                           <td>{displayValue(row.decided_at)}</td>
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>

//                 ) : (
//                   /* DEFAULT TABLE FOR OTHER TABS */
//                   <table>
//                     <thead>
//                       <tr>
//                         {Object.keys(rows[0]).slice(0, 8).map(key => (
//                           <th key={key}>
//                             {formatColumn(key)}
//                           </th>
//                         ))}
//                       </tr>
//                     </thead>

//                     <tbody>
//                       {rows.map((row, index) => (
//                         <tr key={index}>
//                           {Object.keys(row).slice(0, 8).map(key => (
//                             <td key={key}>
//                               {displayValue(row[key])}
//                             </td>
//                           ))}
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             )}
//           </section>
//         )}

//         {/* FOOTER */}
//         <footer>
//           <span>
//             CartRecover · Abandoned Cart Recovery Platform
//           </span>

//           <span>
//             DEMO DATA · NO LIVE MESSAGES SENT
//           </span>
//         </footer>
//       </main>
//     </div>
//   );
// }


import { useEffect, useState } from 'react';

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from 'recharts';

import {
  ShoppingCart,
  Users,
  Mail,
  IndianRupee,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  LayoutDashboard,
  Package,
  Send,
  ChartNoAxesCombined
} from 'lucide-react';

const API = 'http://127.0.0.1:8000/api';

export default function App() {
  const [data, setData] = useState({});
  const [tab, setTab] = useState('Overview');
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);
  // Consent management filters
const [consentSearch, setConsentSearch] = useState('');
const [consentChannel, setConsentChannel] = useState('ALL');
const [consentStatus, setConsentStatus] = useState('ALL');

  // Campaign creation form state
  const [campaignForm, setCampaignForm] = useState({
    campaign_name: '',
    channel: 'EMAIL',
    variant: 'A',
    target_audience: 'ABANDONED_CARTS',
    scheduled_at: ''
  });
  const [campaignSubmitting, setCampaignSubmitting] = useState(false);
  const [campaignMessage, setCampaignMessage] = useState('');
  const [campaignError, setCampaignError] = useState('');
  // Campaign editing state
const [editingCampaign, setEditingCampaign] = useState(null);
const [editSubmitting, setEditSubmitting] = useState(false);
const [editMessage, setEditMessage] = useState('');
const [editError, setEditError] = useState('');

  // Load dashboard data
  const load = async () => {
    try {
      setErr('');

      const response = await fetch(API + '/dashboard');

      if (!response.ok) {
        throw new Error(await response.text());
      }

      setData(await response.json());
    } catch (error) {
      setErr(error.message || 'API unavailable');
    }
  };

  // Load records for the selected tab
  const loadRows = async (selectedTab) => {
    const endpoints = {
      Customers: '/customers',
      Carts: '/carts',
      Campaigns: '/campaigns',
      'Send History': '/sends',
      Orders: '/orders?limit=500',
      Anomalies: '/anomalies',
      'Audit Decisions': '/audit-decisions?limit=500',
      'Consent Management': '/consents?limit=1000'
    };

    if (!endpoints[selectedTab]) {
      setRows([]);
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(API + endpoints[selectedTab]);

      if (!response.ok) {
        throw new Error('Unable to fetch records');
      }

      const result = await response.json();
      setRows(Array.isArray(result) ? result : []);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial dashboard loading
  useEffect(() => {
    load();
  }, []);

  // Load records whenever the selected tab changes
  useEffect(() => {
    loadRows(tab);
  }, [tab]);

  // Navigation items
  const nav = [
    ['Overview', LayoutDashboard],
    ['Customers', Users],
    ['Carts', ShoppingCart],
    ['Campaigns', Send],
    ['Send History', Mail],
    ['Orders', Package],
    ['Anomalies', AlertTriangle],
    // ['Audit Decisions', ShieldCheck]
    ['Audit Decisions', ShieldCheck],
    ['Consent Management', ShieldCheck]
  ];

  // Dashboard metrics
  const metrics = [
    ['Customers', data.customers, Users],
    ['Total carts', data.carts, ShoppingCart],
    ['Abandoned', data.abandoned_carts, AlertTriangle],
    ['Recovered', data.recovered_carts, RefreshCw],
    ['Messages delivered', data.messages_delivered, Mail],
    ['Orders', data.orders, Package],
    ['Attributed orders', data.attributed_orders, ChartNoAxesCombined],
    [
      'Recovered revenue',
      `₹${(data.recovered_revenue || 0).toLocaleString('en-IN')}`,
      IndianRupee
    ]
  ];

  // Messaging funnel data
  const chart = [
    {
      name: 'Attempted',
      value: data.messages_attempted || 0
    },
    {
      name: 'Delivered',
      value: data.messages_delivered || 0
    },
    {
      name: 'Opened',
      value: data.messages_opened || 0
    },
    {
      name: 'Clicked',
      value: data.messages_clicked || 0
    }
  ];

  // Refresh dashboard and current table
  const refreshData = () => {
    load();

    if (tab !== 'Overview') {
      loadRows(tab);
    }
  };

  // Display values safely
  const displayValue = (value) => {
    return value == null ? '—' : String(value);
  };

  // Format table column names
  const formatColumn = (key) => {
    return key.replace(/_/g, ' ');
  };
  // Consent management summary and filtering
const consentOptedIn = rows.filter(
  row => row.status === 'OPTED_IN'
).length;

const consentOptedOut = rows.filter(
  row => row.status === 'OPTED_OUT'
).length;

const filteredConsentRows = rows.filter(row => {
  const search = consentSearch.toLowerCase();

  const matchesSearch =
    String(row.customer_name || '').toLowerCase().includes(search) ||
    String(row.customer_id || '').toLowerCase().includes(search);

  const matchesChannel =
    consentChannel === 'ALL' || row.channel === consentChannel;

  const matchesStatus =
    consentStatus === 'ALL' || row.status === consentStatus;

  return matchesSearch && matchesChannel && matchesStatus;
});

  // Create a draft campaign through the FastAPI endpoint.
  const createCampaign = async (event) => {
    event.preventDefault();
    setCampaignSubmitting(true);
    setCampaignMessage('');
    setCampaignError('');

    try {
      const payload = {
        ...campaignForm,
        // datetime-local already provides local YYYY-MM-DDTHH:mm format.
        // Append seconds while keeping the selected local time unchanged.
        scheduled_at: campaignForm.scheduled_at.length === 16
          ? `${campaignForm.scheduled_at}:00`
          : campaignForm.scheduled_at
      };

      const response = await fetch(API + '/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || 'Campaign creation failed.');
      }

      setCampaignMessage(
        `Campaign created successfully. ID: ${result.campaign_id} (DRAFT)`
      );
      setCampaignForm({
        campaign_name: '',
        channel: 'EMAIL',
        variant: 'A',
        target_audience: 'ABANDONED_CARTS',
        scheduled_at: ''
      });
      await loadRows('Campaigns');
      await load();
    } catch (error) {
      setCampaignError(error.message || 'Unable to create campaign.');
    } finally {
      setCampaignSubmitting(false);
    }
  };
    // Open a campaign for editing
  const startEditCampaign = (campaign) => {
    setEditingCampaign({
      ...campaign,
      scheduled_at: campaign.scheduled_at
        ? String(campaign.scheduled_at).slice(0, 16)
        : ''
    });

    setEditMessage('');
    setEditError('');
  };

  // Save campaign changes through the PATCH API
  const updateCampaign = async (event) => {
    event.preventDefault();

    if (!editingCampaign) return;

    setEditSubmitting(true);
    setEditMessage('');
    setEditError('');

    try {
      const payload = {
        campaign_name: editingCampaign.campaign_name,
        channel: editingCampaign.channel,
        variant: editingCampaign.variant,
        target_audience: editingCampaign.target_audience,
        scheduled_at: editingCampaign.scheduled_at.length === 16
          ? `${editingCampaign.scheduled_at}:00`
          : editingCampaign.scheduled_at
      };

      const response = await fetch(
        `${API}/campaigns/${encodeURIComponent(editingCampaign.campaign_id)}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Campaign update failed.');
      }

      setEditMessage(
        `Campaign ${result.campaign_id} updated successfully.`
      );

      setEditingCampaign(null);

      await loadRows('Campaigns');
      await load();

    } catch (error) {
      setEditError(error.message || 'Unable to update campaign.');
    } finally {
      setEditSubmitting(false);
    }
  };

  return (
    <div className="shell">

      {/* SIDEBAR */}
      <aside>
        <div className="brand">
          <div className="brandicon">
            CR
          </div>

          <div>
            <b>CartRecover</b>
            <small>COMMERCE INTELLIGENCE</small>
          </div>
        </div>

        <div className="navlabel">
          WORKSPACE
        </div>

        {nav.map(([name, Icon]) => (
          <button
            className={tab === name ? 'active' : ''}
            onClick={() => setTab(name)}
            key={name}
          >
            <Icon size={18} />
            {name}
          </button>
        ))}

        <div className="sidebottom">
          <ShieldCheck size={18} />

          Consent-first orchestration

          <small>
            MySQL · Local environment
          </small>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main>

        {/* HEADER */}
        <header>
          <div>
            <span className="eyebrow">
              OPERATIONS / {tab.toUpperCase()}
            </span>

            <h1>
              {tab === 'Overview' ? 'Recovery overview' : tab}
            </h1>

            <p>
              Monitor recovery performance, customer permissions and conversion outcomes.
            </p>
          </div>

          <button
            className="refresh"
            onClick={refreshData}
          >
            <RefreshCw size={16} />
            Refresh data
          </button>
        </header>

        {/* ERROR MESSAGE */}
        {err && (
          <div className="error">
            <AlertTriangle size={18} />

            <div>
              <b>Backend connection unavailable</b>
              <br />
              {err}
              <br />
              Start MySQL, load the starter dataset, then run FastAPI.
            </div>
          </div>
        )}

        {/* OVERVIEW DASHBOARD */}
        {tab === 'Overview' ? (
          <>
            {/* METRIC CARDS */}
            <section className="metrics">
              {metrics.map(([name, value, Icon]) => (
                <div className="metric" key={name}>
                  <div className="metrichead">
                    <span>{name}</span>
                    <Icon size={18} />
                  </div>

                  <strong>
                    {value ?? 0}
                  </strong>

                  <small>
                    Live database metric
                  </small>
                </div>
              ))}
            </section>

            {/* CHARTS */}
            <section className="charts">

              {/* MESSAGING FUNNEL */}
              <div className="panel">
                <div className="paneltitle">
                  <div>
                    <b>Messaging funnel</b>
                    <small>
                      Communication event progression
                    </small>
                  </div>

                  <span className="pill">
                    ALL CHANNELS
                  </span>
                </div>

                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={chart}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />

                    <Bar
                      dataKey="value"
                      fill="#5367e8"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* CART LIFECYCLE */}
              <div className="panel">
                <div className="paneltitle">
                  <div>
                    <b>Cart lifecycle</b>
                    <small>
                      Current cart distribution
                    </small>
                  </div>
                </div>

                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={[
                        {
                          name: 'Abandoned',
                          value: data.abandoned_carts || 0
                        },
                        {
                          name: 'Active',
                          value: data.active_carts || 0
                        },
                        {
                          name: 'Recovered',
                          value: data.recovered_carts || 0
                        }
                      ]}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={62}
                      outerRadius={92}
                      paddingAngle={4}
                    >
                      {[0, 1, 2].map(index => (
                        <Cell
                          key={index}
                          fill={['#5367e8', '#19a88b', '#f2a64b'][index]}
                        />
                      ))}
                    </Pie>

                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* BUSINESS RULES */}
            <section className="panel insight">
              <div>
                <b>
                  <ShieldCheck size={18} />
                  Consent and suppression guardrails
                </b>

                <p>
                  Messages are eligible only when the latest effective
                  channel consent is OPTED_IN. Unknown and withdrawn
                  consent is suppressed.
                </p>
              </div>

              <div>
                <b>
                  <ChartNoAxesCombined size={18} />
                  Attribution policy
                </b>

                <p>
                  Single-touch, 7-day attribution. A qualifying click
                  outranks open and delivery; one order receives at
                  most one campaign credit.
                </p>
              </div>
            </section>
          </>
        ) : tab === 'Campaigns' ? (
          /* CAMPAIGN MANAGEMENT AND CREATE CAMPAIGN */
          <div>
            <section className="panel" style={{ marginBottom: 20 }}>
              <div className="paneltitle">
                <div>
                  <b>Create a recovery campaign</b>
                  <small>Create a draft campaign. No messages are sent from this form.</small>
                </div>
              </div>

              <form
                onSubmit={createCampaign}
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
                  gap: 14,
                  padding: 16
                }}
              >
                <label style={{ display: 'grid', gap: 7 }}>
                  <span>Campaign name</span>
                  <input
                    type="text"
                    required
                    maxLength={120}
                    value={campaignForm.campaign_name}
                    onChange={event => setCampaignForm({ ...campaignForm, campaign_name: event.target.value })}
                    placeholder="e.g. Weekend Cart Recovery"
                    style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
                  />
                </label>

                <label style={{ display: 'grid', gap: 7 }}>
                  <span>Channel</span>
                  <select
                    value={campaignForm.channel}
                    onChange={event => setCampaignForm({ ...campaignForm, channel: event.target.value })}
                    style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', font: 'inherit' }}
                  >
                    <option value="EMAIL">Email</option>
                    <option value="SMS">SMS</option>
                  </select>
                </label>

                <label style={{ display: 'grid', gap: 7 }}>
                  <span>Variant</span>
                  <select
                    value={campaignForm.variant}
                    onChange={event => setCampaignForm({ ...campaignForm, variant: event.target.value })}
                    style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', font: 'inherit' }}
                  >
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                  </select>
                </label>

                <label style={{ display: 'grid', gap: 7 }}>
                  <span>Target audience</span>
                  <input
                    type="text"
                    required
                    maxLength={120}
                    value={campaignForm.target_audience}
                    onChange={event => setCampaignForm({ ...campaignForm, target_audience: event.target.value })}
                    style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
                  />
                </label>

                <label style={{ display: 'grid', gap: 7 }}>
                  <span>Scheduled at</span>
                  <input
                    type="datetime-local"
                    required
                    value={campaignForm.scheduled_at}
                    onChange={event => setCampaignForm({ ...campaignForm, scheduled_at: event.target.value })}
                    style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
                  />
                </label>

                <div style={{ display: 'flex', alignItems: 'end' }}>
                  <button
                    type="submit"
                    disabled={campaignSubmitting}
                    style={{ padding: '11px 18px', border: 0, borderRadius: 8, background: '#5367e8', color: '#fff', font: 'inherit', cursor: campaignSubmitting ? 'wait' : 'pointer', opacity: campaignSubmitting ? 0.7 : 1 }}
                  >
                    {campaignSubmitting ? 'Creating...' : 'Create draft campaign'}
                  </button>
                </div>
              </form>

              {campaignMessage && (
                <div style={{ margin: '0 16px 16px', padding: 12, borderRadius: 8, background: '#e8f7ef', color: '#176b3a' }}>
                  {campaignMessage}
                </div>
              )}
              {campaignError && (
                <div style={{ margin: '0 16px 16px', padding: 12, borderRadius: 8, background: '#fff0f0', color: '#a12626' }}>
                  {campaignError}
                </div>
              )}
            </section>

            {editingCampaign && (
              <section className="panel" style={{ marginBottom: 20 }}>
                <div className="paneltitle">
                  <div>
                    <b>Edit Campaign - {editingCampaign.campaign_id}</b>
                    <small>Only draft campaigns can be edited.</small>
                  </div>
                </div>

                <form
                  onSubmit={updateCampaign}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
                    gap: 14,
                    padding: 16
                  }}
                >
                  <label style={{ display: 'grid', gap: 7 }}>
                    <span>Campaign name</span>
                    <input
                      type="text"
                      required
                      maxLength={120}
                      value={editingCampaign.campaign_name || ''}
                      onChange={event => setEditingCampaign({ ...editingCampaign, campaign_name: event.target.value })}
                      style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
                    />
                  </label>

                  <label style={{ display: 'grid', gap: 7 }}>
                    <span>Channel</span>
                    <select
                      value={editingCampaign.channel || 'EMAIL'}
                      onChange={event => setEditingCampaign({ ...editingCampaign, channel: event.target.value })}
                      style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', font: 'inherit' }}
                    >
                      <option value="EMAIL">Email</option>
                      <option value="SMS">SMS</option>
                    </select>
                  </label>

                  <label style={{ display: 'grid', gap: 7 }}>
                    <span>Variant</span>
                    <select
                      value={editingCampaign.variant || 'A'}
                      onChange={event => setEditingCampaign({ ...editingCampaign, variant: event.target.value })}
                      style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', font: 'inherit' }}
                    >
                      <option value="A">A</option>
                      <option value="B">B</option>
                      <option value="C">C</option>
                    </select>
                  </label>

                  <label style={{ display: 'grid', gap: 7 }}>
                    <span>Target audience</span>
                    <input
                      type="text"
                      required
                      maxLength={120}
                      value={editingCampaign.target_audience || ''}
                      onChange={event => setEditingCampaign({ ...editingCampaign, target_audience: event.target.value })}
                      style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
                    />
                  </label>

                  <label style={{ display: 'grid', gap: 7 }}>
                    <span>Scheduled at</span>
                    <input
                      type="datetime-local"
                      required
                      value={editingCampaign.scheduled_at || ''}
                      onChange={event => setEditingCampaign({ ...editingCampaign, scheduled_at: event.target.value })}
                      style={{ padding: 11, border: '1px solid #dce1ed', borderRadius: 8, font: 'inherit' }}
                    />
                  </label>

                  <div style={{ display: 'flex', alignItems: 'end', gap: 10 }}>
                    <button
                      type="submit"
                      disabled={editSubmitting}
                      style={{ padding: '11px 18px', border: 0, borderRadius: 8, background: '#5367e8', color: '#fff', font: 'inherit', cursor: editSubmitting ? 'wait' : 'pointer', opacity: editSubmitting ? 0.7 : 1 }}
                    >
                      {editSubmitting ? 'Saving...' : 'Save Changes'}
                    </button>

                    <button
                      type="button"
                      disabled={editSubmitting}
                      onClick={() => { setEditingCampaign(null); setEditError(''); setEditMessage(''); }}
                      style={{ padding: '11px 18px', border: '1px solid #dce1ed', borderRadius: 8, background: '#fff', color: '#333', font: 'inherit', cursor: 'pointer' }}
                    >
                      Cancel
                    </button>
                  </div>

                  {editError && (
                    <div style={{ gridColumn: '1 / -1', padding: 12, borderRadius: 8, background: '#fff0f0', color: '#a12626' }}>
                      {editError}
                    </div>
                  )}
                </form>
              </section>
            )}

            {editMessage && !editingCampaign && (
              <div style={{ marginBottom: 16, padding: 12, borderRadius: 8, background: '#e8f7ef', color: '#176b3a' }}>
                {editMessage}
              </div>
            )}

            <section className="panel tablepanel">
              <div className="paneltitle">
                <div>
                  <b>Campaigns</b>
                  <small>Campaign records from the MySQL database</small>
                </div>
                <span className="pill">{rows.length} RECORDS</span>
              </div>

              {loading ? (
                <div className="empty">Loading campaigns...</div>
              ) : rows.length === 0 ? (
                <div className="empty">No campaigns found. Create your first draft campaign above.</div>
              ) : (
                <div className="tablewrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Campaign ID</th>
                        <th>Campaign Name</th>
                        <th>Channel</th>
                        <th>Variant</th>
                        <th>Target Audience</th>
                        <th>Scheduled At</th>
                        <th>Status</th>
                        <th>Created At</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row, index) => (
                        <tr key={row.campaign_id || index}>
                          <td>{displayValue(row.campaign_id)}</td>
                          <td>{displayValue(row.campaign_name)}</td>
                          <td>{displayValue(row.channel)}</td>
                          <td>{displayValue(row.variant)}</td>
                          <td>{displayValue(row.target_audience)}</td>
                          <td>{displayValue(row.scheduled_at)}</td>
                          <td>{displayValue(row.status)}</td>
                          <td>{displayValue(row.created_at)}</td>
                          <td>
                            {row.status === 'DRAFT' ? (
                              <button
                                type="button"
                                onClick={() => startEditCampaign(row)}
                                style={{
                                  padding: '7px 12px',
                                  border: '1px solid #5367e8',
                                  borderRadius: 6,
                                  background: '#fff',
                                  color: '#5367e8',
                                  cursor: 'pointer'
                                }}
                              >
                                Edit
                              </button>
                            ) : (
                              'Not editable'
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        ) : tab === 'Consent Management' ? (
          /* CONSENT MANAGEMENT */
          <div>
            <section className="metrics">
              <div className="metric">
                <div className="metrichead">
                  <span>Total consent records</span>
                  <ShieldCheck size={18} />
                </div>
                <strong>{rows.length}</strong>
                <small>Records from the database</small>
              </div>

              <div className="metric">
                <div className="metrichead">
                  <span>Opted in</span>
                  <ShieldCheck size={18} />
                </div>
                <strong>{consentOptedIn}</strong>
                <small>Permission granted</small>
              </div>

              <div className="metric">
                <div className="metrichead">
                  <span>Opted out</span>
                  <AlertTriangle size={18} />
                </div>
                <strong>{consentOptedOut}</strong>
                <small>Permission withdrawn</small>
              </div>
            </section>

            <section className="panel" style={{ marginBottom: 20 }}>
              <div className="paneltitle">
                <div>
                  <b>Search and filter consents</b>
                  <small>Search by customer and filter by channel or status</small>
                </div>
              </div>

              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 12,
                padding: 16
              }}>
                <input
                  type="text"
                  value={consentSearch}
                  onChange={event => setConsentSearch(event.target.value)}
                  placeholder="Search customer name or ID"
                  style={{
                    flex: '2 1 220px',
                    minWidth: 200,
                    padding: 11,
                    border: '1px solid #dce1ed',
                    borderRadius: 8,
                    font: 'inherit'
                  }}
                />

                <select
                  value={consentChannel}
                  onChange={event => setConsentChannel(event.target.value)}
                  style={{
                    flex: '1 1 150px',
                    padding: 11,
                    border: '1px solid #dce1ed',
                    borderRadius: 8,
                    background: '#fff',
                    font: 'inherit'
                  }}
                >
                  <option value="ALL">All channels</option>
                  <option value="EMAIL">Email</option>
                  <option value="SMS">SMS</option>
                </select>

                <select
                  value={consentStatus}
                  onChange={event => setConsentStatus(event.target.value)}
                  style={{
                    flex: '1 1 150px',
                    padding: 11,
                    border: '1px solid #dce1ed',
                    borderRadius: 8,
                    background: '#fff',
                    font: 'inherit'
                  }}
                >
                  <option value="ALL">All statuses</option>
                  <option value="OPTED_IN">Opted in</option>
                  <option value="OPTED_OUT">Opted out</option>
                </select>
              </div>
            </section>

            <section className="panel tablepanel">
              <div className="paneltitle">
                <div>
                  <b>Customer consent records</b>
                  <small>Consent history stored in MySQL</small>
                </div>
                <span className="pill">
                  {filteredConsentRows.length} RECORDS
                </span>
              </div>

              {loading ? (
                <div className="empty">Loading consent records...</div>
              ) : (
                <div className="tablewrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Consent ID</th>
                        <th>Customer ID</th>
                        <th>Customer Name</th>
                        <th>Channel</th>
                        <th>Status</th>
                        <th>Effective At</th>
                        <th>Withdrawn At</th>
                        <th>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredConsentRows.map((row, index) => (
                        <tr key={row.consent_id || index}>
                          <td>{displayValue(row.consent_id)}</td>
                          <td>{displayValue(row.customer_id)}</td>
                          <td>{displayValue(row.customer_name)}</td>
                          <td>{displayValue(row.channel)}</td>
                          <td>{displayValue(row.status)}</td>
                          <td>{displayValue(row.effective_at)}</td>
                          <td>{displayValue(row.withdrawn_at)}</td>
                          <td>{displayValue(row.source)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {filteredConsentRows.length === 0 && (
                    <div className="empty">
                      No consent records match the selected filters.
                    </div>
                  )}
                </div>
              )}
            </section>
          </div>
        ) : (
          /* DATA TABLES */
          <section className="panel tablepanel">
            <div className="paneltitle">
              <div>
                <b>{tab}</b>
                <small>
                  Records from the MySQL database
                </small>
              </div>

              <span className="pill">
                {rows.length} RECORDS
              </span>
            </div>

            {loading ? (
              <div className="empty">
                Loading records...
              </div>
            ) : rows.length === 0 ? (
              <div className="empty">
                No records available. Check the database connection and load the dataset.
              </div>
            ) : (
              <div className="tablewrap">

                {/* SPECIAL ORDERS TABLE */}
                {tab === 'Orders' ? (
                  <table>
                    <thead>
                      <tr>
                        <th>Order ID</th>
                        <th>Customer ID</th>
                        <th>Order Total</th>
                        <th>Ordered At</th>
                        <th>Attribution Status</th>
                        <th>Attribution ID</th>
                        <th>Campaign ID</th>
                        <th>Send ID</th>
                        <th>Attributed Revenue</th>
                      </tr>
                    </thead>

                    <tbody>
                      {rows.map((row, index) => {
                        const attributed = row.attribution_id != null;

                        return (
                          <tr key={index}>
                            <td>{displayValue(row.order_id)}</td>
                            <td>{displayValue(row.customer_id)}</td>
                            <td>
                              ₹{Number(row.order_total || 0).toLocaleString('en-IN')}
                            </td>
                            <td>{displayValue(row.ordered_at)}</td>
                            <td>
                              {attributed ? 'Attributed' : 'Not Attributed'}
                            </td>
                            <td>
                              {row.attribution_id ?? 'Not Attributed'}
                            </td>
                            <td>
                              {row.attributed_campaign_id ?? 'Not Attributed'}
                            </td>
                            <td>
                              {row.attributed_send_id ?? 'Not Attributed'}
                            </td>
                            <td>
                              {attributed
                                ? `₹${Number(row.attributed_revenue || 0).toLocaleString('en-IN')}`
                                : '—'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>

                ) : tab === 'Audit Decisions' ? (
                  /* SPECIAL AUDIT DECISIONS TABLE */
                  <table>
                    <thead>
                      <tr>
                        <th>Decision ID</th>
                        <th>Customer ID</th>
                        <th>Cart ID</th>
                        <th>Channel</th>
                        <th>Decision</th>
                        <th>Reason Code</th>
                        <th>Explanation</th>
                        <th>Decided At</th>
                      </tr>
                    </thead>

                    <tbody>
                      {rows.map((row, index) => (
                        <tr key={index}>
                          <td>{displayValue(row.decision_id)}</td>
                          <td>{displayValue(row.customer_id)}</td>
                          <td>{displayValue(row.cart_id)}</td>
                          <td>{displayValue(row.channel)}</td>
                          <td>{displayValue(row.decision)}</td>
                          <td>{displayValue(row.reason_code)}</td>
                          <td>{displayValue(row.detail)}</td>
                          <td>{displayValue(row.decided_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                ) : (
                  /* DEFAULT TABLE FOR OTHER TABS */
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(rows[0]).slice(0, 8).map(key => (
                          <th key={key}>
                            {formatColumn(key)}
                          </th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      {rows.map((row, index) => (
                        <tr key={index}>
                          {Object.keys(row).slice(0, 8).map(key => (
                            <td key={key}>
                              {displayValue(row[key])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </section>
        )}

        {/* FOOTER */}
        <footer>
          <span>
            CartRecover · Abandoned Cart Recovery Platform
          </span>

          <span>
            DEMO DATA · NO LIVE MESSAGES SENT
          </span>
        </footer>
      </main>
    </div>
  );
}
