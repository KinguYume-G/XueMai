import React from 'react';
import { Steps, Card, Progress, Typography, Space, Tag } from 'antd';
import {
    LoadingOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    ClockCircleOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

// TypeScript interfaces
export interface WorkflowStep {
    id: string;
    name: string;
    status: 'pending' | 'running' | 'success' | 'error';
    result?: {
        success: boolean;
        data_keys?: string[];
    };
    startTime?: number;
    endTime?: number;
}

export interface WorkflowProgressProps {
    steps: WorkflowStep[];
    workflowName?: string;
    isRunning: boolean;
    elapsedTime?: number; // in milliseconds
}

// Utility: Format duration from milliseconds to readable format
const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`;
    const seconds = (ms / 1000).toFixed(1);
    return `${seconds}s`;
};

// Calculate overall progress percentage
const calculateProgress = (steps: WorkflowStep[]): number => {
    if (steps.length === 0) return 0;
    const completedSteps = steps.filter(
        (step) => step.status === 'success' || step.status === 'error'
    ).length;
    return Math.round((completedSteps / steps.length) * 100);
};

// Get icon based on step status
const getStepIcon = (status: WorkflowStep['status']) => {
    switch (status) {
        case 'pending':
            return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
        case 'running':
            return <LoadingOutlined style={{ color: '#1890ff' }} spin />;
        case 'success':
            return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
        case 'error':
            return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
    }
};

// Get status color
const getStatusColor = (status: WorkflowStep['status']): string => {
    switch (status) {
        case 'pending':
            return 'default';
        case 'running':
            return 'processing';
        case 'success':
            return 'success';
        case 'error':
            return 'error';
    }
};

export const WorkflowProgress: React.FC<WorkflowProgressProps> = ({
    steps,
    workflowName = 'AI Workflow',
    isRunning,
    elapsedTime,
}) => {
    const progress = calculateProgress(steps);
    const currentStepIndex = steps.findIndex((step) => step.status === 'running');

    return (
        <Card
            title={
                <Space direction="vertical" size={0} style={{ width: '100%' }}>
                    <Title level={4} style={{ margin: 0 }}>
                        {workflowName}
                    </Title>
                    {isRunning && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                            执行中... {progress}% 完成
                        </Text>
                    )}
                    {!isRunning && progress === 100 && (
                        <Tag color="success" style={{ marginTop: 4 }}>
                            工作流完成
                        </Tag>
                    )}
                    {elapsedTime !== undefined && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                            总用时: {formatDuration(elapsedTime)}
                        </Text>
                    )}
                </Space>
            }
            style={{ marginBottom: 16 }}
        >
            {isRunning && (
                <Progress
                    percent={progress}
                    status={progress === 100 ? 'success' : 'active'}
                    style={{ marginBottom: 20 }}
                />
            )}

            <Steps
                direction="vertical"
                current={currentStepIndex >= 0 ? currentStepIndex : steps.length}
                items={steps.map((step) => {
                    const duration =
                        step.startTime && step.endTime
                            ? formatDuration(step.endTime - step.startTime)
                            : '';

                    return {
                        title: (
                            <Space>
                                <span style={{ fontWeight: step.status === 'running' ? 600 : 400 }}>
                                    {step.name}
                                </span>
                                <Tag color={getStatusColor(step.status)} style={{ marginLeft: 8 }}>
                                    {step.status === 'pending' && '等待中'}
                                    {step.status === 'running' && '执行中'}
                                    {step.status === 'success' && '完成'}
                                    {step.status === 'error' && '失败'}
                                </Tag>
                            </Space>
                        ),
                        description: duration ? (
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                耗时: {duration}
                            </Text>
                        ) : undefined,
                        status:
                            step.status === 'error'
                                ? 'error'
                                : step.status === 'success'
                                    ? 'finish'
                                    : step.status === 'running'
                                        ? 'process'
                                        : 'wait',
                        icon: getStepIcon(step.status),
                    };
                })}
            />
        </Card>
    );
};
