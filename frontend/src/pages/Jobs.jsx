import { useState, useEffect } from 'react';
import api from '../api/axios';
import ApplyButton from '../components/ApplyButton';
import { Search, MapPin, DollarSign, Briefcase } from 'lucide-react';

const Jobs = () => {
    const [jobs, setJobs] = useState([]);
    const [search, setSearch] = useState("");

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const res = await api.get('/jobs');
            setJobs(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const filteredJobs = jobs.filter(job =>
        job.title?.toLowerCase().includes(search.toLowerCase()) ||
        job.company?.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div>
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-gray-800">Job Marketplace</h2>
                <div className="relative">
                    <input
                        type="text"
                        placeholder="Search jobs..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="pl-10 pr-4 py-2 border rounded-full w-64 focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                    />
                    <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                </div>
            </div>

            <div className="grid gap-6">
                {filteredJobs.map(job => (
                    <div key={job.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                                <div className="text-primary font-medium mb-2">{job.company}</div>
                                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                                    <span className="flex items-center"><MapPin className="w-4 h-4 mr-1" /> {job.location || 'Remote'}</span>
                                    {job.salary_max && (
                                        <span className="flex items-center"><DollarSign className="w-4 h-4 mr-1" /> {job.salary_min / 1000}k - {job.salary_max / 1000}k</span>
                                    )}
                                    <span className="flex items-center"><Briefcase className="w-4 h-4 mr-1" /> {job.source}</span>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {job.tags && job.tags.slice(0, 4).map(tag => (
                                        <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div className="flex flex-col items-end space-y-2">
                                <div className="text-xs text-gray-400 mb-2">Posted {new Date(job.created_at).toLocaleDateString()}</div>
                                <ApplyButton jobId={job.id} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            {filteredJobs.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                    No jobs found.
                </div>
            )}
        </div>
    );
};

export default Jobs;
