import { useState } from 'react';
import api from '../api/axios';
import { Send, Loader2 } from 'lucide-react';

const ApplyButton = ({ jobId, onApplied }) => {
    const [loading, setLoading] = useState(false);

    const handleApply = async (e) => {
        e.stopPropagation();
        if (!confirm("Are you sure you want to auto-apply to this job?")) return;

        setLoading(true);
        try {
            await api.post(`/automation/apply/${jobId}`);
            alert("Auto-application triggered!");
            if (onApplied) onApplied();
        } catch (err) {
            console.error(err);
            alert("Failed to start application.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleApply}
            disabled={loading}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-primary to-indigo-600 text-white rounded-md hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 transition shadow-sm"
        >
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
            {loading ? 'Applying...' : 'Auto Apply'}
        </button>
    );
};

export default ApplyButton;
