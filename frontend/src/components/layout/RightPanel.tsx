import React from 'react';
import { ArrowRight, Lock, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';

const RightPanel: React.FC = () => {
  const schoolZones = [
    { name: 'APU 专区', locked: false },
    { name: '清华大学专区', locked: true },
    { name: '北京大学专区', locked: true },
  ];

  const hotTopics = [
    '#AI论文写作技巧',
    '#马来西亚实习避坑指南',
    '#跨文化交流经验',
    '#2024秋季交换项目',
  ];

  const exchangeReminders = [
    {
      project: '新加坡国立大学交换',
      deadline: '2024-10-15',
      urgent: true,
    },
    {
      project: '香港大学暑期项目',
      deadline: '2024-11-01',
      urgent: false,
    },
  ];

  return (
    <div className="p-4 space-y-6">
      {/* School Zones */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">学校专区</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {schoolZones.map((zone, index) => (
            <Button
              key={index}
              variant="ghost"
              className={`w-full justify-between h-auto p-3 ${
                zone.locked ? 'text-gray-400 cursor-not-allowed' : 'text-gray-700 hover:bg-gray-50'
              }`}
              disabled={zone.locked}
            >
              <span className="text-sm font-medium">{zone.name}</span>
              {zone.locked ? (
                <Lock className="h-4 w-4" />
              ) : (
                <ArrowRight className="h-4 w-4" />
              )}
            </Button>
          ))}
        </CardContent>
      </Card>

      {/* Hot Topics */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">热门话题</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {hotTopics.map((topic, index) => (
            <Button
              key={index}
              variant="ghost"
              className="w-full justify-start h-auto p-2 text-blue-600 hover:bg-blue-50"
            >
              <span className="text-sm">{topic}</span>
            </Button>
          ))}
        </CardContent>
      </Card>

      {/* Exchange Project Reminders */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">交换项目提醒</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {exchangeReminders.map((reminder, index) => (
            <div
              key={index}
              className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50"
            >
              <Calendar className={`h-5 w-5 mt-0.5 ${reminder.urgent ? 'text-red-500' : 'text-gray-400'}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {reminder.project}
                </p>
                <p className={`text-xs mt-1 ${reminder.urgent ? 'text-red-600' : 'text-gray-500'}`}>
                  截止日期: {reminder.deadline}
                </p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default RightPanel;
