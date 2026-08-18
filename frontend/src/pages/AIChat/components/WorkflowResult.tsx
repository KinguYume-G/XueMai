import React, { useState } from 'react';
import { Card, Button, Skeleton, Typography, Space, message } from 'antd';
import { CopyOutlined, ReloadOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';

const { Title, Text, Paragraph } = Typography;

interface WorkflowResultProps {
    result: {
        answer: string;
        metadata?: Record<string, any>;
    } | null;
    isLoading: boolean;
    onRetry?: () => void;
}

export const WorkflowResult: React.FC<WorkflowResultProps> = ({
    result,
    isLoading,
    onRetry,
}) => {
    const [copying, setCopying] = useState(false);

    const handleCopy = async () => {
        if (!result?.answer) return;

        setCopying(true);
        try {
            await navigator.clipboard.writeText(result.answer);
            message.success('结果已复制到剪贴板');
        } catch (error) {
            message.error('复制失败');
        } finally {
            setCopying(false);
        }
    };

    return (
        <Card
            title={
                <Space>
                    <Title level={4} style={{ margin: 0 }}>
                        AI分析结果
                    </Title>
                </Space>
            }
            extra={
                result && (
                    <Space>
                        <Button
                            icon={<CopyOutlined />}
                            onClick={handleCopy}
                            loading={copying}
                            size="small"
                        >
                            复制
                        </Button>
                        {onRetry && (
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={onRetry}
                                size="small"
                            >
                                重新生成
                            </Button>
                        )}
                    </Space>
                )
            }
            style={{ marginTop: 16 }}
        >
            {isLoading ? (
                <Skeleton active paragraph={{ rows: 6 }} />
            ) : result ? (
                <div>
                    {/* Markdown content */}
                    <div
                        style={{
                            fontSize: '14px',
                            lineHeight: '1.8',
                            color: '#262626',
                        }}
                        className="workflow-result-markdown"
                    >
                        <ReactMarkdown
                            components={{
                                h1: ({ node, ...props }) => (
                                    <Title level={3} style={{ marginTop: 24, marginBottom: 16 }} {...props} />
                                ),
                                h2: ({ node, ...props }) => (
                                    <Title level={4} style={{ marginTop: 20, marginBottom: 12 }} {...props} />
                                ),
                                h3: ({ node, ...props }) => (
                                    <Title level={5} style={{ marginTop: 16, marginBottom: 8 }} {...props} />
                                ),
                                p: ({ node, ...props }) => (
                                    <Paragraph style={{ marginBottom: 12 }} {...props} />
                                ),
                                ul: ({ node, ...props }) => (
                                    <ul style={{ paddingLeft: 24, marginBottom: 12 }} {...props} />
                                ),
                                ol: ({ node, ...props }) => (
                                    <ol style={{ paddingLeft: 24, marginBottom: 12 }} {...props} />
                                ),
                                code: ({ node, inline, ...props }: any) =>
                                    inline ? (
                                        <code
                                            style={{
                                                backgroundColor: '#f5f5f5',
                                                padding: '2px 6px',
                                                borderRadius: 3,
                                                fontFamily: 'Monaco, Consolas, monospace',
                                                fontSize: '0.9em',
                                            }}
                                            {...props}
                                        />
                                    ) : (
                                        <pre
                                            style={{
                                                backgroundColor: '#f5f5f5',
                                                padding: 12,
                                                borderRadius: 4,
                                                overflowX: 'auto',
                                                marginBottom: 12,
                                            }}
                                        >
                                            <code
                                                style={{
                                                    fontFamily: 'Monaco, Consolas, monospace',
                                                    fontSize: '0.9em',
                                                }}
                                                {...props}
                                            />
                                        </pre>
                                    ),
                            }}
                        >
                            {result.answer}
                        </ReactMarkdown>
                    </div>

                    {/* Metadata section */}
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                        <div
                            style={{
                                marginTop: 24,
                                padding: 16,
                                backgroundColor: '#fafafa',
                                borderRadius: 4,
                                borderLeft: '3px solid #1890ff',
                            }}
                        >
                            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 600 }}>
                                处理详情
                            </Text>
                            <div style={{ marginTop: 8 }}>
                                {Object.entries(result.metadata).map(([key, value]) => (
                                    <div key={key} style={{ marginBottom: 4 }}>
                                        <Text type="secondary" style={{ fontSize: '12px' }}>
                                            {key}: {String(value)}
                                        </Text>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <Text type="secondary">暂无结果</Text>
            )}
        </Card>
    );
};
