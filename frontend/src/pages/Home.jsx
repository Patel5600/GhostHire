import { useNavigate } from 'react-router-dom';

const DashboardHome = () => {
    const navigate = useNavigate();

    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome back, User!</h1>
            <p className="text-gray-500 mb-8">Here is what's happening with your job search today.</p>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[
                    { label: 'Total Applications', value: '12', color: 'bg-blue-500' },
                    { label: 'Interviews', value: '3', color: 'bg-purple-500' },
                    { label: 'Offers', value: '1', color: 'bg-green-500' },
                    { label: 'Rejections', value: '4', color: 'bg-red-500' }
                ].map((stat) => (
                    <div key={stat.label} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="text-gray-500 text-sm mb-1">{stat.label}</div>
                        <div className="text-3xl font-bold text-gray-800">{stat.value}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="font-semibold text-lg mb-4">Recommended Jobs</h3>
                    <div className="space-y-4">
                        <div className="text-gray-400 text-sm text-center py-8">
                            Complete your profile to get AI recommendations.
                        </div>
                        <button onClick={() => navigate('/jobs')} className="w-full py-2 text-primary text-sm font-medium hover:bg-gray-50 rounded-lg">
                            Browse All Jobs
                        </button>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="font-semibold text-lg mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="flex items-center text-sm">
                                <div className="w-2 h-2 bg-primary rounded-full mr-3"></div>
                                <span className="text-gray-600">Applied to <span className="font-medium text-gray-900">Engineering Manager</span> at <span className="font-medium text-gray-900">TechCorp</span></span>
                                <span className="ml-auto text-gray-400 text-xs">2h ago</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardHome;
