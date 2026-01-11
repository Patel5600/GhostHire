import { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { Upload, FileText, Trash2, CheckCircle } from 'lucide-react';

const Resumes = () => {
    const [resumes, setResumes] = useState([]);
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        fetchResumes();
    }, []);

    const fetchResumes = async () => {
        try {
            const res = await api.get('/resumes');
            // Assuming endpoint returns list of resumes
            // Adjust according to actual backend response structure: e.g. res.data
            setResumes(Array.isArray(res.data) ? res.data : []);
        } catch (err) {
            console.error(err);
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        try {
            await api.post('/resumes/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            fetchResumes();
        } catch (err) {
            console.error("Upload failed", err);
            alert("Upload failed.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">My Resumes</h2>
                <label className="flex items-center px-4 py-2 bg-primary text-white rounded-md cursor-pointer hover:bg-indigo-700 transition">
                    <Upload className="w-4 h-4 mr-2" />
                    {uploading ? 'Uploading...' : 'Upload New'}
                    <input type="file" className="hidden" accept=".pdf,.docx" onChange={handleUpload} disabled={uploading} />
                </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {resumes.map((resume) => (
                    <div key={resume.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="flex items-start justify-between">
                            <div className="flex items-center">
                                <div className="p-2 bg-indigo-50 rounded-lg mr-4">
                                    <FileText className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900 truncate max-w-[200px]">{resume.file_name || `Resume #${resume.id}`}</h3>
                                    <p className="text-xs text-gray-500">Uploaded on {new Date(resume.created_at).toLocaleDateString()}</p>
                                </div>
                            </div>
                        </div>
                        <div className="mt-4 pt-4 border-t flex justify-between items-center">
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full flex items-center">
                                <CheckCircle className="w-3 h-3 mr-1" /> Parsed
                            </span>
                            <button className="text-red-500 hover:bg-red-50 p-1 rounded">
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            {resumes.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                    No resumes found. Upload one to get started.
                </div>
            )}
        </div>
    );
};

export default Resumes;
