import { sendScreenshot, startStep } from '../services/apiService';

const SUPABASE_URL = 'https://nynhpfozeopaaqkczcqs.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55bmhwZm96ZW9wYWFxa2N6Y3FzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzNTAxNTQsImV4cCI6MjA3NjkyNjE1NH0.Cn9Ke-dEiTVxQryfqI3MeuLruKUpV8bgjK-p3w7fKIE';

async function fetchFromSupabase(table, filters = {}) {
    let url = `${SUPABASE_URL}/rest/v1/${table}?select=*`;
    
    // Add filters to URL
    Object.keys(filters).forEach(key => {
        url += `&${key}=eq.${filters[key]}`;
    });
    
    const response = await fetch(url, {
        headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        console.error(`Failed to fetch from ${table}:`, response.status, response.statusText);
        return [];
    }
    
    return await response.json();
}

async function updateSupabase(table, id, data) {
    const url = `${SUPABASE_URL}/rest/v1/${table}?id=eq.${id}`;
    
    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        },
        body: JSON.stringify(data)
    });
    
    return response.ok;
}

export default async function connect() {
    // COMMENTED OUT - Using backend-managed state instead
    // const lessons = await fetchFromSupabase('lesson', { is_finished: false });
    // console.log('Lessons data:', lessons);
    
    // if (!Array.isArray(lessons) || lessons.length === 0) {
    //     console.log('No lessons found or lessons is not an array');
    //     return;
    // }
    
    // for (const lesson of lessons) {
    //     const steps = await fetchFromSupabase('step', { lesson_id: lesson.id });
    //     console.log('Steps data:', steps);
        
    //     if (!Array.isArray(steps) || steps.length === 0) {
    //         console.log(`No steps found for lesson ${lesson.id} or steps is not an array`);
    //         continue;
    //     }
        
    //     for (const step of steps) {
    //         let completed = false;
    //         while (!completed) {
    //             await new Promise(r => setTimeout(r, 10000)); // Wait 10 seconds
    //             const res = await sendScreenshot();
    //             if (res?.data?.completed) {
    //                 completed = true;
    //             }
    //         }
    //     }
        
    //     await updateSupabase('lesson', lesson.id, { is_finished: true });
    // }
    
    console.log('connect() called - function disabled, using backend-managed learning flow');
}
// connect(); // Disabled - not auto-starting