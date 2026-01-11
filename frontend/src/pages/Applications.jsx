import { useState, useEffect } from 'react';
import api from '../api/axios';
import { PlayCircle, CheckCircle, XCircle, Clock } from 'lucide-react';
import { clsx } from 'clsx';

const StatusBadge = ({ status }) => {
    const styles = {
        saved: "bg-gray-100 text-gray-700",
        applying: "bg-blue-100 text-blue-700",
        applied: "bg-green-100 text-green-700",
        failed: "bg-red-100 text-red-700",
        interviewing: "bg-purple-100 text-purple-700",
        rejected: "bg-red-50 text-red-600"
    };

    const icons = {
        saved: Clock,
        applying: Clock,
        applied: CheckCircle,
        failed: XCircle,
        interviewing: PlayCircle,
        rejected: XCircle
    };

    const Icon = icons[status] || Clock;

    return (
        <span className={clsx("px-2.5 py-0.5 rounded-full text-xs font-medium flex items-center w-fit", styles[status] || styles.saved)}>
            <Icon className="w-3 h-3 mr-1" />
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

const Applications = () => {
    const [applications, setApplications] = useState([]);

    useEffect(() => {
        const fetchApps = async () => {
            try {
                // Mock endpoint or real one if exists. 
                // Assuming we have GET /applications
                // If not, we'd need to add it to backend. 
                // For now, I'll simulate or try to fetch.
                const res = await api.get('/applications');
                setApplications(res.data);
            } catch (err) {
                console.error("Failed to load applications", err);
            }
        };
        fetchApps();
    }, []);

    return (
        <div>
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Application Tracker</h2>
            <div className="bg-white rounded-lg shadowoverflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {applications.map((app) => (
                            <tr key={app.id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">{app.job?.title || 'Unknown Job'}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-500">{app.job?.company || 'Unknown Status'}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-500">{new Date(app.created_at).toLocaleDateString()}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <StatusBadge status={app.status || 'saved'} />
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button className="text-indigo-600 hover:text-indigo-900">View</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {applications.length === 0 && (
                    <div className="p-6 text-center text-gray-500">No applications found.</div>
                )}
            </div>
        </div>
    );
};

export default Applications;
