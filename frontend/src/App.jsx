import React, { useState, useEffect } from 'react';
import { Upload, Shirt, Search, Sparkles } from 'lucide-react';

const API_URL = 'http://localhost:8000'; // Change for production

export default function ThriftMatchmaker() {
  const [wardrobe, setWardrobe] = useState([]);
  const [matches, setMatches] = useState(null);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('wardrobe'); // 'wardrobe' or 'match'
  const [userId] = useState('default_user'); // Add auth later

  // Load wardrobe on mount
  useEffect(() => {
    loadWardrobe();
  }, []);

  const loadWardrobe = async () => {
    try {
      const res = await fetch(`${API_URL}/wardrobe/${userId}`);
      const data = await res.json();
      setWardrobe(data.items);
    } catch (err) {
      console.error('Failed to load wardrobe:', err);
    }
  };

  const uploadWardrobeItem = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    try {
      const res = await fetch(`${API_URL}/wardrobe/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      
      if (data.success) {
        await loadWardrobe();
        alert('Item added to wardrobe!');
      }
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const matchThriftItem = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    try {
      const res = await fetch(`${API_URL}/match/thrift`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setMatches(data);
      setView('match');
    } catch (err) {
      alert('Match failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      if (type === 'wardrobe') {
        uploadWardrobeItem(file);
      } else {
        matchThriftItem(file);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shirt className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Thrift Matchmaker</h1>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setView('wardrobe')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  view === 'wardrobe'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                My Wardrobe ({wardrobe.length})
              </button>
              
              <button
                onClick={() => setView('match')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  view === 'match'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Find Matches
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {view === 'wardrobe' ? (
          <WardrobeView 
            wardrobe={wardrobe} 
            onUpload={handleFileUpload}
            loading={loading}
          />
        ) : (
          <MatchView 
            matches={matches}
            wardrobe={wardrobe}
            onUpload={handleFileUpload}
            loading={loading}
          />
        )}
      </main>
    </div>
  );
}

function WardrobeView({ wardrobe, onUpload, loading }) {
  return (
    <div>
      <div className="mb-8 bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Upload Your Clothes</h2>
        <p className="text-gray-600 mb-4">
          Build your digital wardrobe by uploading photos of your clothing items.
        </p>
        
        <label className="cursor-pointer inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
          <Upload className="h-5 w-5 mr-2" />
          {loading ? 'Uploading...' : 'Upload Item'}
          <input
            type="file"
            accept="image/*"
            onChange={(e) => onUpload(e, 'wardrobe')}
            className="hidden"
            disabled={loading}
          />
        </label>
      </div>

      {wardrobe.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Shirt className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No items yet</h3>
          <p className="text-gray-500">Upload your first clothing item to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {wardrobe.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition">
              <div className="aspect-square bg-gray-100 flex items-center justify-center">
                <Shirt className="h-12 w-12 text-gray-400" />
              </div>
              <div className="p-3">
                <p className="font-medium text-sm capitalize">{item.category}</p>
                <div className="flex items-center mt-1 space-x-2">
                  <div 
                    className="w-4 h-4 rounded-full border border-gray-300"
                    style={{ backgroundColor: item.color_primary }}
                  />
                  <span className="text-xs text-gray-500 capitalize">{item.color_primary}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MatchView({ matches, wardrobe, onUpload, loading }) {
  return (
    <div>
      <div className="mb-8 bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Find Matching Items</h2>
        <p className="text-gray-600 mb-4">
          Upload a thrift item photo to see which items from your wardrobe match it.
        </p>
        
        <label className="cursor-pointer inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
          <Search className="h-5 w-5 mr-2" />
          {loading ? 'Analyzing...' : 'Upload Thrift Item'}
          <input
            type="file"
            accept="image/*"
            onChange={(e) => onUpload(e, 'thrift')}
            className="hidden"
            disabled={loading}
          />
        </label>
      </div>

      {matches ? (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center mb-4">
              <Sparkles className="h-5 w-5 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold">Match Results</h3>
            </div>
            
            {matches.matches.length === 0 ? (
              <p className="text-gray-500">No matches found. This item might not pair well with your current wardrobe.</p>
            ) : (
              <>
                <p className="text-gray-700 mb-4">
                  Found {matches.matches.length} matching items in your wardrobe!
                </p>
                
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                  {matches.matches.map((match, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4 border-2 border-purple-200">
                      <div className="aspect-square bg-white rounded mb-2 flex items-center justify-center">
                        <Shirt className="h-10 w-10 text-gray-400" />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Match</span>
                        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                          {Math.round(match.score * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="font-medium mb-2">Outfit Ideas:</h4>
                  <ul className="space-y-1">
                    {matches.outfit_ideas.map((idea, idx) => (
                      <li key={idx} className="text-sm text-gray-700">• {idea}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Upload a thrift item</h3>
          <p className="text-gray-500">We'll show you which items from your wardrobe match it</p>
        </div>
      )}
    </div>
  );
}